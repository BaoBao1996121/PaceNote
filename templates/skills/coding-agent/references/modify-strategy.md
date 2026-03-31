# 文件修改策略

> 当任务的操作类型为"修改"时，必须遵循本文档的策略，精准编辑现有文件。
> **核心原则：永远不覆盖整个文件，只做最小化的精准修改。**

---

## 修改流程

```
┌──────────────────────────────────────────────────────────┐
│  Step 1: 读取现有文件                                     │
│  read_file(targetFile, 1, END) → existingCode            │
├──────────────────────────────────────────────────────────┤
│  Step 2: 定位锚点                                         │
│  根据骨架中的类名/方法名/命名空间，在现有代码中找到位置      │
├──────────────────────────────────────────────────────────┤
│  Step 3: 确定修改类型                                     │
│  A. 插入新代码（新方法、新属性、新 include）                │
│  B. 替换现有代码（修改方法实现、更新逻辑）                  │
│  C. 包裹现有代码（添加 try-catch、条件判断等）              │
├──────────────────────────────────────────────────────────┤
│  Step 4: 执行编辑                                         │
│  使用 replace_string_in_file 精准替换                     │
├──────────────────────────────────────────────────────────┤
│  Step 5: 验证                                             │
│  re-read 修改后的文件确认正确性                            │
└──────────────────────────────────────────────────────────┘
```

---

## 锚点定位规则

### 什么是锚点？

锚点是现有代码中能唯一标识修改位置的代码片段。

```
好的锚点：                              差的锚点：
- class MyService {                    - {
- void ProcessData(                    - return;
- namespace {{PLATFORM_NAMESPACE}}.VOI              - // TODO
- #include "{{PLATFORM_NS_PREFIX}}VOI.h"                - using System;
```

### 定位策略

| 修改类型 | 锚点定位方式 | 示例 |
|----------|-------------|------|
| 新增方法 | 找到类定义的末尾 `}` | 在最后一个方法之后、类闭合 `}` 之前插入 |
| 修改方法 | 找到方法签名 | `public void ProcessData(` |
| 新增属性 | 找到属性区域 | 在最后一个属性声明之后 |
| 新增 include/using | 找到已有的 include/using 块 | 在最后一个 `#include` 之后 |
| 新增接口实现 | 找到类声明行 | `class MyService : IService` → 添加新接口 |

---

## replace_string_in_file 使用规范

### 1. 上下文行数要求

**最少 3 行上下文**，确保唯一匹配：

```csharp
// ✅ 好的 — 足够的上下文
oldString = """
    public void ExistingMethod()
    {
        // existing implementation
    }

    private int _count;
"""

newString = """
    public void ExistingMethod()
    {
        // existing implementation
    }

    public void NewMethod()
    {
        // new implementation
    }

    private int _count;
"""
```

```csharp
// ❌ 差的 — 上下文不足，可能匹配多处
oldString = """
    }
"""
```

### 2. 保持缩进一致

```csharp
// ✅ 匹配现有文件的缩进风格
// 如果现有文件用 4 空格缩进，新代码也用 4 空格
newString = """
    public void NewMethod()
    {
        var result = Calculate();
        return result;
    }
"""

// ❌ 不要混用 Tab 和空格
```

### 3. 多处修改时的顺序

当一个文件需要多处修改时，**从文件底部向顶部**修改，避免行号偏移：

```
修改列表（按新代码插入位置排序）：
1. 第 150 行 — 新增方法      ← 最后执行
2. 第 80 行  — 修改方法实现   ← 其次执行
3. 第 5 行   — 新增 using     ← 最先执行（从底部开始）

实际执行顺序: 1 → 2 → 3（从底部到顶部）
```

---

## 常见修改模式

### 模式 A：在类中新增方法

```
锚点：类的最后一个方法的闭合大括号 + 类的闭合大括号
策略：在两者之间插入新方法
```

```csharp
// oldString（包含最后一个方法的结尾和类的结尾）
oldString = """
        return result;
    }
} // end of class
"""

// newString（在中间插入新方法）
newString = """
        return result;
    }

    /// <summary>
    /// 新增的方法描述
    /// </summary>
    public void NewMethod()
    {
        // implementation
    }
} // end of class
"""
```

### 模式 B：修改方法实现

```
锚点：方法签名 + 方法体
策略：替换整个方法体
```

```csharp
// oldString（完整的方法）
oldString = """
    public int Calculate(int x)
    {
        return x * 2;
    }
"""

// newString（修改后的方法）
newString = """
    public int Calculate(int x)
    {
        if (x <= 0)
        {
            // 🔴 HUMAN_CHECK: 负数情况是否应该抛异常？
            return 0;
        }
        return x * 2 + _offset;
    }
"""
```

### 模式 C：新增 using/include

```
锚点：现有的 using/include 块
策略：在块的末尾添加新行
```

```csharp
// oldString
oldString = """
using System.Linq;
using System.Threading.Tasks;

namespace {{PLATFORM_NAMESPACE}}
"""

// newString
newString = """
using System.Linq;
using System.Threading.Tasks;
using {{PLATFORM_NAMESPACE}}.Export;

namespace {{PLATFORM_NAMESPACE}}
"""
```

### 模式 D：包裹现有代码

```
锚点：需要包裹的代码段
策略：在前后添加包裹代码
```

```csharp
// oldString
oldString = """
    var data = LoadData(path);
    ProcessData(data);
"""

// newString
newString = """
    try
    {
        var data = LoadData(path);
        ProcessData(data);
    }
    catch (IOException ex)
    {
        Logger.Error($"数据加载失败: {ex.Message}");
        // 🔴 HUMAN_CHECK: 异常后是否需要回滚操作？
        throw;
    }
"""
```

---

## C++ 修改模式

> 平台层任务（层级 = 平台BE）通常涉及 C++ 代码，需注意头/源文件对和命名空间。

### 模式 E：新增 #include

```cpp
// oldString
oldString = """
#include "{{PLATFORM_NS_PREFIX}}VOI/VOIHelper.h"
#include "{{PLATFORM_NS_PREFIX}}VOI/VOIDefines.h"

namespace {{PLATFORM_NS}} {
"""

// newString
newString = """
#include "{{PLATFORM_NS_PREFIX}}VOI/VOIHelper.h"
#include "{{PLATFORM_NS_PREFIX}}VOI/VOIDefines.h"
#include "{{PLATFORM_NS_PREFIX}}VOI/ExportHelper.h"

namespace {{PLATFORM_NS}} {
"""
```

### 模式 F：在类中新增方法（头文件 + 源文件成对）

头文件声明（`.h`）：

```cpp
// oldString
oldString = """
    bool ProcessData(const DataParam& param);

private:
    int m_nCount;
"""

// newString
newString = """
    bool ProcessData(const DataParam& param);
    
    /// \brief 导出数据到指定路径
    /// \param strPath 导出目标路径
    /// \return 导出是否成功
    bool ExportData(const std::string& strPath);

private:
    int m_nCount;
"""
```

源文件实现（`.cpp`）：

```cpp
// oldString（文件末尾的命名空间闭合）
oldString = """
    return true;
}

} // namespace {{PLATFORM_NS}}
"""

// newString
newString = """
    return true;
}

bool VOIHelper::ExportData(const std::string& strPath)
{
    // 🔴 HUMAN_CHECK: 路径编码是否需要 UTF-8 转换？
    if (strPath.empty())
    {
        LOG_ERROR("ExportData: path is empty");
        return false;
    }
    
    // 实现导出逻辑
    return true;
}

} // namespace {{PLATFORM_NS}}
"""
```

### 模式 G：修改现有 C++ 方法

```cpp
// oldString
oldString = """
bool VOIHelper::ProcessData(const DataParam& param)
{
    if (!param.IsValid())
    {
        return false;
    }
    return DoProcess(param);
}
"""

// newString
newString = """
bool VOIHelper::ProcessData(const DataParam& param)
{
    if (!param.IsValid())
    {
        LOG_WARN("ProcessData: invalid param");
        return false;
    }
    
    // 🔴 HUMAN_CHECK: 是否需要在 DoProcess 前加锁？多线程场景下可能有竞争
    auto result = DoProcess(param);
    if (!result)
    {
        LOG_ERROR("ProcessData: DoProcess failed");
    }
    return result;
}
"""
```

> **C++ 特有注意事项：**
> - 新增方法时，**头文件声明 + 源文件实现必须成对修改**
> - 命名空间使用 `namespace {{PLATFORM_NS}} { ... }` 风格（不用 `namespace {{PLATFORM_NS}}::VOI`）
> - 日志用 `LOG_ERROR` / `LOG_WARN`（项目宏）
> - 字符串参数用 `const std::string&`
> - 注释用 `/// \brief` Doxygen 风格

---

## 禁止事项

| 禁止 | 原因 | 正确做法 |
|------|------|----------|
| 用 `create_file` 覆盖已有文件 | 丢失未被骨架覆盖的代码 | 用 `replace_string_in_file` |
| 猜测文件内容做替换 | oldString 不匹配导致失败 | 先 `read_file` 再替换 |
| 一次替换超过 50 行 | 风险过大 | 拆分为多次小替换 |
| 修改不相关的代码 | 超出任务范围 | 只改骨架指定的部分 |
| 删除现有注释或文档 | 丢失上下文 | 保留原有注释 |

---

## HUMAN_CHECK 触发条件

在修改任务中，以下情况**必须**添加 HUMAN_CHECK：

1. **找不到精确锚点** — 不确定应该在哪个位置插入
2. **现有代码与骨架冲突** — 骨架假设的结构与实际不一致
3. **涉及多个文件联动** — 修改此处可能影响其他文件
4. **删除现有逻辑** — 骨架要求替换掉现有实现
5. **命名空间/类型不确定** — 不确定应该引用哪个具体类型

```csharp
// 🔴 HUMAN_CHECK: 在 line 85 和 line 120 都找到了 ProcessData 方法，不确定应该修改哪一个
// 🔴 HUMAN_CHECK: 骨架要求添加 IExportService 参数，但现有方法已有 3 个参数，确认接口兼容性
```
