# 电商平台功能模块清单

> 📅 生成日期: 2026-01-15
> 📊 模块总数: 6 个

## 模块列表

| # | 模块名称 | 英文标识 | 职责描述 | 触发关键词 | 关键类/文件 | 所属层级 |
|---|---------|---------|---------|-----------|------------|---------|
| 1 | 购物车 | shopping-cart | 管理商品加购、数量修改、优惠计算和结算 | 购物车, cart, 加购, 结算, SKU | `CartService.ts`, `PriceCalculator.ts` | 应用层 |
| 2 | 订单 | order | 管理订单创建、状态流转、退款处理 | 订单, order, 下单, 退款, refund | `OrderService.ts`, `OrderStateMachine.ts` | 应用层 |
| 3 | 支付 | payment | 对接支付渠道、处理支付回调、对账 | 支付, payment, 付款, pay | `PaymentService.ts`, `PaymentGateway.ts` | 应用层 |
| 4 | 商品 | product | 商品管理、SKU、分类、搜索 | 商品, product, SKU, 分类, 搜索 | `ProductService.ts`, `SearchIndex.ts` | 应用层 |
| 5 | 用户 | user | 用户注册、登录、权限、会员等级 | 用户, user, 登录, 注册, 权限 | `UserService.ts`, `AuthMiddleware.ts` | 应用层 |
| 6 | 促销 | promotion | 优惠券、满减活动、限时折扣 | 促销, promotion, 优惠券, 满减, 折扣 | `PromotionEngine.ts`, `CouponService.ts` | 应用层 |

## 模块分组

### 交易核心
- 购物车 — 加购到结算的完整流程
- 订单 — 订单生命周期管理
- 支付 — 支付渠道对接与对账

### 商品域
- 商品 — 商品信息和搜索
- 促销 — 营销活动引擎

### 基础服务
- 用户 — 账户和权限体系
