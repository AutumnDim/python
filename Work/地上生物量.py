# -*- coding: utf-8 -*-
"""
Created on Tue Sep  2 14:57:51 2025

@author: 中科院地理所
"""


'''模型'''
# -*- coding: utf-8 -*-
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# import warnings
# warnings.filterwarnings('ignore')
# from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
# from sklearn.pipeline import Pipeline
# from sklearn.preprocessing import StandardScaler
# from sklearn.feature_selection import SelectKBest, mutual_info_regression
# from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
# from sklearn.linear_model import LinearRegression, Ridge, Lasso
# from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
# from xgboost import XGBRegressor
# from sklearn.base import clone
# import joblib
# from pathlib import Path

# # 中文绘图设置（可选）
# plt.rcParams['font.sans-serif'] = ['SimHei']   # 若无黑体可改为其他中文字体
# plt.rcParams['axes.unicode_minus'] = False


# path = r"E:\地上生物量\提取特征\特征值.csv"
# datak = pd.read_csv(path, encoding='gbk')
# datak = datak.dropna(how='any').copy()


# y = datak.iloc[:, 0].values          # 目标变量
# X = datak.iloc[:, 1:].values         # 特征矩阵
# feature_names = datak.columns[1:].tolist()
# target_name = datak.columns[0]

# print("=" * 60)
# print("深度数据诊断与分析")
# print("=" * 60)
# print(f"样本数量: {len(y)}")
# print(f"特征数量: {X.shape[1]}")
# print(f"目标变量 - {target_name}:")
# print(f"  范围: [{y.min():.4f}, {y.max():.4f}]")
# print(f"  均值±标准差: {y.mean():.4f} ± {y.std():.4f}")
# print(f"  中位数: {np.median(y):.4f}")
# print(f"  偏度: {pd.Series(y).skew():.4f}")
# print(f"  峰度: {pd.Series(y).kurtosis():.4f}")


# #目标分布可视化

# plt.figure(figsize=(15, 10))

# plt.subplot(2, 3, 1)
# plt.hist(y, bins=20, alpha=0.7, edgecolor='black')
# plt.title('目标变量分布')
# plt.xlabel('值'); plt.ylabel('频数')

# plt.subplot(2, 3, 2)
# plt.boxplot(y)
# plt.title('目标变量箱线图')

# plt.subplot(2, 3, 3)
# plt.hist(np.log1p(y), bins=20, alpha=0.7, color='green', edgecolor='black')
# plt.title('对数变换后分布')
# plt.xlabel('log(1+值)')


# #  相关性分析

# correlations = []
# for i in range(X.shape[1]):
#     if np.std(X[:, i]) > 0:
#         corr = np.corrcoef(X[:, i], y)[0, 1]
#         correlations.append((feature_names[i], corr))
# correlations.sort(key=lambda x: abs(x[1]), reverse=True)

# print("\n=== 特征与目标变量相关性排名 ===")
# for i, (name, corr) in enumerate(correlations[:10]):
#     print(f"{i+1}. {name}: {corr:.4f}")

# plt.subplot(2, 3, 4)
# corr_values = [c for _, c in correlations[:10]]
# feature_names_top = [n for n, _ in correlations[:10]]
# plt.barh(range(len(corr_values)), corr_values)
# plt.yticks(range(len(corr_values)), feature_names_top)
# plt.title('Top 10 特征相关性')
# plt.xlabel('相关系数')


# # 目标对数变换
# '''对生物量数据进行对数变换，降低偏态与异方差性，使模型更易于学习'''
# y_log = np.log1p(y)  


# # 训练/测试划分（分层依据：y_log分箱）
# def make_bins_for_stratify(y_arr, q=5):
#     labels = pd.qcut(y_arr, q=min(q, max(3, len(y_arr)//10)), labels=False, duplicates='drop')
#     return labels
# y_bins_full = make_bins_for_stratify(y_log, q=5)
# X_train, X_test, y_train, y_test = train_test_split(
#     X, y_log, test_size=0.15, stratify=y_bins_full, random_state=42)
# '''通过将目标变量分箱后分层抽样，确保训练集和测试集在目标分布上的一致性，避免随机划分带来的评估偏差'''

# # 展示的互信息排名（在训练集上计算，避免泄漏）
# '''在训练集上计算特征与目标的互信息，排序展示特征重要性。随后在模型训练中，
#   使用标准化+互信息选特征 的Pipeline，并在交叉验证内部完成，避免信息泄漏'''
# scaler_tmp = StandardScaler()
# X_train_scaled_tmp = scaler_tmp.fit_transform(X_train)
# mi_scores = mutual_info_regression(X_train_scaled_tmp, y_train, random_state=42)
# mi_indices = np.argsort(mi_scores)[::-1]
# print("\n=== 基于互信息的特征重要性排名（仅训练集） ===")
# for i in range(min(10, len(feature_names))):
#     print(f"{i+1}. {feature_names[mi_indices[i]]}: {mi_scores[mi_indices[i]]:.4f}")
# # 构建 预处理+选特征 Pipeline（在CV内执行，避免泄漏）
# top_k = min(10, X.shape[1])
# preprocess = Pipeline([
#     ('scaler', StandardScaler()),
#     ('select', SelectKBest(score_func=mutual_info_regression, k=top_k))
# ])


# # 为回归构造分层CV索引
# from sklearn.model_selection import StratifiedKFold
# def make_stratified_regression_splits(X_, y_, n_splits=5, random_state=42):
#     bins = make_bins_for_stratify(y_, q=min(5, len(y_)//2 if len(y_)>=10 else 3))
#     n_splits_eff = min(n_splits, len(np.unique(bins)))
#     n_splits_eff = max(n_splits_eff, 3)  # 至少3折
#     skf = StratifiedKFold(n_splits=n_splits_eff, shuffle=True, random_state=random_state)
#     return list(skf.split(X_, bins))

# cv_splits = make_stratified_regression_splits(X_train, y_train, n_splits=5, random_state=42)


# # 多算法比较（CV均值-方差稳健准则）
# def build_model_pipelines(preprocess_pipe):
#     models = {
#         'Linear Regression': LinearRegression(),
#         'Ridge Regression': Ridge(alpha=1.0),
#         'Lasso Regression': Lasso(alpha=0.1),
#         'Random Forest': RandomForestRegressor(
#             n_estimators=300, min_samples_leaf=2, random_state=42
#         ),
#         'Gradient Boosting': GradientBoostingRegressor(
#             n_estimators=300, random_state=42
#         ),
#         'XGBoost': XGBRegressor(
#             n_estimators=500, max_depth=4, subsample=0.8, colsample_bytree=0.8,
#             reg_alpha=0.0, reg_lambda=1.5, learning_rate=0.05,
#             objective='reg:squarederror', random_state=42
#         )
#     }
#     pipes = {}
#     for name, base in models.items():
#         pipes[name] = Pipeline([
#             ('preprocess', preprocess_pipe),
#             ('model', base)
#         ])
#     return pipes

# def test_different_models(X_tr, y_tr, X_te, y_te, preprocess_pipe, cv_index_splits):
#     from sklearn.base import clone
#     pipes = build_model_pipelines(preprocess_pipe)
#     results = {}
#     print("\n=== 不同算法性能比较 ===")
#     for name, model in pipes.items():
#         try:
#             cv_scores = cross_val_score(model, X_tr, y_tr, cv=cv_index_splits, scoring='r2', n_jobs=-1)
#             model.fit(X_tr, y_tr)
#             y_pred = model.predict(X_te)
#             test_r2 = r2_score(y_te, y_pred)
#             results[name] = {
#                 'CV_R2_mean': float(np.mean(cv_scores)),
#                 'CV_R2_std': float(np.std(cv_scores)),
#                 'Test_R2': float(test_r2),
#                 'model': clone(model).fit(X_tr, y_tr)
#             }
#             print(f"{name:20s}: CV R² = {np.mean(cv_scores):.3f} ± {np.std(cv_scores):.3f}, Test R² = {test_r2:.3f}")
#         except Exception as e:
#             print(f"{name:20s}: 错误 - {str(e)}")
#             results[name] = None
#     return results

# results = test_different_models(X_train, y_train, X_test, y_test, preprocess, cv_splits)

# # 选择最佳算法（mean - std 最大）
# valid_results = {k: v for k, v in results.items() if v is not None}
# if valid_results:
#     def score_fn(res): return res['CV_R2_mean'] - res['CV_R2_std']
#     best_model_name, best_info = max(valid_results.items(), key=lambda kv: score_fn(kv[1]))
#     final_model = best_info['model']  # 已拟合Pipeline
#     print(f"\n选择最佳算法: {best_model_name} (基于CV性能与稳定性)")
# else:
#     best_model_name = "Random Forest"
#     final_model = Pipeline([
#         ('preprocess', preprocess),
#         ('model', RandomForestRegressor(n_estimators=300, min_samples_leaf=2, random_state=42))
#     ]).fit(X_train, y_train)
#     print("没有有效的模型结果，使用默认的随机森林")


# # 在原尺度计算指标
# def evaluate_model(y_true_log, y_pred_log, use_log_transform=True):
#     if use_log_transform:
#         y_true = np.expm1(y_true_log)
#         y_pred = np.expm1(y_pred_log)
#     else:
#         y_true = y_true_log
#         y_pred = y_pred_log

#     mse = mean_squared_error(y_true, y_pred)
#     rmse = np.sqrt(mse)
#     mae = mean_absolute_error(y_true, y_pred)
#     r2 = r2_score(y_true, y_pred)

#     mask = y_true > 0.1
#     mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100 if np.any(mask) else np.nan
#     rrmse = (rmse / np.mean(y_true)) * 100 if np.mean(y_true) != 0 else np.nan
#     return mse, rmse, mae, r2, mape, rrmse

# train_pred_log = final_model.predict(X_train)
# test_pred_log  = final_model.predict(X_test)

# train_metrics = evaluate_model(y_train, train_pred_log, True)
# test_metrics  = evaluate_model(y_test,  test_pred_log,  True)

# print("\n" + "="*60)
# print("最终模型评估结果")
# print("="*60)
# print(f'算法: {best_model_name}')
# print('训练集: MSE={:.3f}, RMSE={:.3f}, MAE={:.3f}, R²={:.3f}, MAPE={:.3f}%, RRMSE={:.3f}%'.format(*train_metrics))
# print('测试集: MSE={:.3f}, RMSE={:.3f}, MAE={:.3f}, R²={:.3f}, MAPE={:.3f}%, RRMSE={:.3f}%'.format(*test_metrics))

# # 特征重要性（树模型可用）
# def plot_feature_importance_if_available(pipeline_model, feature_names_all):
#     model_step = pipeline_model.named_steps['model']
#     if not hasattr(model_step, 'feature_importances_'):
#         return

#     selector = pipeline_model.named_steps['preprocess'].named_steps['select']
#     support_mask = selector.get_support()
#     selected_names = [name for name, keep in zip(feature_names_all, support_mask) if keep]

#     importances = model_step.feature_importances_
#     indices = np.argsort(importances)[::-1]

#     print("\n=== 特征重要性排名 ===")
#     top_n = min(10, len(selected_names))
#     for i in range(top_n):
#         print(f"{i+1}. {selected_names[indices[i]]}: {importances[indices[i]]:.4f}")

#     plt.figure(figsize=(10, 6))
#     plt.barh(range(len(selected_names)), importances[indices])
#     plt.yticks(range(len(selected_names)), [selected_names[i] for i in indices])
#     plt.xlabel('特征重要性'); plt.title('特征重要性排名')
#     plt.tight_layout()
#     plt.show()

# plot_feature_importance_if_available(final_model, feature_names)

# # 可视化：预测-实际、残差、学习曲线
# plt.figure(figsize=(15, 5))

# y_test_original = np.expm1(y_test)
# test_pred_original = np.expm1(test_pred_log)

# plt.subplot(1, 3, 1)
# plt.scatter(y_test_original, test_pred_original, alpha=0.6)
# max_val = max(y_test_original.max(), test_pred_original.max())
# plt.plot([0, max_val], [0, max_val], 'r--', lw=2)
# plt.xlabel('实际值'); plt.ylabel('预测值')
# plt.title(f'预测 vs 实际 (R2={r2_score(y_test_original, test_pred_original):.3f})')

# plt.subplot(1, 3, 2)
# residuals = y_test_original - test_pred_original
# plt.scatter(test_pred_original, residuals, alpha=0.6)
# plt.axhline(y=0, color='r', linestyle='--')
# plt.xlabel('预测值'); plt.ylabel('残差')
# plt.title('残差分析')

# def build_final_pipeline_by_name(name, preprocess_pipe):
#     if name == "Random Forest":
#         base = RandomForestRegressor(n_estimators=300, min_samples_leaf=2, random_state=42)
#     elif name == "XGBoost":
#         base = XGBRegressor(
#             n_estimators=500, max_depth=4, subsample=0.8, colsample_bytree=0.8,
#             reg_alpha=0.0, reg_lambda=1.5, learning_rate=0.05,
#             objective='reg:squarederror', random_state=42
#         )
#     elif name == "Gradient Boosting":
#         base = GradientBoostingRegressor(n_estimators=300, random_state=42)
#     elif name == "Ridge Regression":
#         base = Ridge(alpha=1.0)
#     elif name == "Lasso Regression":
#         base = Lasso(alpha=0.1)
#     else:
#         base = LinearRegression()
#     return Pipeline([('preprocess', preprocess_pipe), ('model', base)])

# plt.subplot(1, 3, 3)
# train_sizes = np.linspace(0.2, 1.0, 9)
# train_scores = []
# test_scores = []
# for size in train_sizes:
#     n_size = max(5, int(len(X_train) * size))
#     X_subset = X_train[:n_size]
#     y_subset = y_train[:n_size]
#     model_lc = build_final_pipeline_by_name(best_model_name, preprocess)
#     model_lc.fit(X_subset, y_subset)
#     y_pred_train = model_lc.predict(X_subset)
#     y_pred_test  = model_lc.predict(X_test)
#     train_scores.append(r2_score(y_subset, y_pred_train))
#     test_scores.append(r2_score(y_test, y_pred_test))

# plt.plot(train_sizes, train_scores, 'o-', label='训练集')
# plt.plot(train_sizes, test_scores, 'o-', label='测试集')
# plt.xlabel('训练集比例'); plt.ylabel('R²得分')
# plt.title('学习曲线')
# plt.legend()
# plt.tight_layout()
# plt.show()

# # =========================
# # 建议输出
# # =========================
# print("\n" + "="*60)
# print("改进建议")
# print("="*60)
# if test_metrics[3] >= 0.7:
#     print("✅ 模型性能良好")
# elif test_metrics[3] >= 0.6:
#     print("✅ 模型性能可接受")
# else:
#     print("⚠️ 需要提升模型性能:")

# print("\n通用建议:")
# print("1. 增加数据量: 收集更多样本是提升性能最有效的方法")
# print("2. 特征工程: 尝试创建多项式特征和交互特征（例如 NDVI×RGR, SAVI×Red）")
# print("3. 异常值处理: 检查并处理极端值的影响")
# print("4. 领域知识: 结合专业知识选择更有意义的特征")
# print("5. 集成方法: 尝试模型集成或堆叠方法")

# if test_metrics[0] > train_metrics[0] * 1.5:
#     print("\n特定建议:")
#     print("📉 模型存在过拟合，建议:")
#     print("   - 增强正则化（例如提升 min_samples_leaf / 降低树深）")
#     print("   - 减少模型复杂度（例如降低 n_estimators 或 max_depth）")
#     print("   - 使用更简单的模型（岭/套索）做对比")
#     print("   - 增加训练数据量")

# if pd.Series(y).skew() > 1.0:
#     print("\n📊 目标变量分布高度偏斜，建议:")
#     print("   - 使用对数变换（已采用）或Box-Cox等")
#     print("   - 尝试分位数回归")
#     print("   - 使用对偏斜分布鲁棒的评估指标（如MSLE、加权MAPE）")

# print("="*60)

# # ====== 保存最终模型与元数据（用于栅格推理） ======
# out_dir = Path(r"E:\地上生物量\提取特征")
# out_dir.mkdir(parents=True, exist_ok=True)

# artifact = {
#     "pipeline": final_model,          # 已拟合 Pipeline（含预处理与特征选择）
#     "best_model_name": best_model_name,
#     "feature_names": feature_names,   # 训练时特征名顺序
#     "target_log1p": True,             # 训练目标是否使用 log1p
# }
# joblib.dump(artifact, out_dir / "agb_model.joblib")
# print(f"[OK] 模型与元数据已保存到 {out_dir/'agb_model.joblib'}")







'''模拟'''
# -*- coding: utf-8 -*-
import os
from pathlib import Path
import numpy as np
import rasterio
from rasterio.windows import Window
from rasterio.enums import Resampling
import joblib
import glob
import re

# ============= 用户配置区 =============
# 1) 模型文件
MODEL_PATH = r"E:\地上生物量\提取特征\agb_model.joblib"

# 2) 特征栅格路径映射：键必须是训练时的 feature_names，值是对应的 10m 栅格路径
# 定义波段顺序
band_order = ["Blue", "CAI", "CRI", "Green", "NDII", "NDVI", "NIR", "RGR", "RVI", "Red", "SATVI", "SAVI", "SWIR1", "SWIR2", "VARI"]

# 获取所有tif文件并排序
feature_rasters = glob.glob(r"E:\地上生物量\地上生物量\7,8\2508\*.tif")

# 创建排序函数
def sort_by_band_name(file_path):
    filename = file_path.split('\\')[-1].lower()  # 获取文件名并转为小写
    
    # 使用正则表达式匹配波段名称
    for i, band in enumerate(band_order):
        if re.search(rf'\b{band.lower()}\b', filename):
            return i
    # 如果没有匹配到任何波段，放在最后
    return len(band_order)

# 按照波段顺序排序
sorted_raster_paths = sorted(feature_rasters, key=sort_by_band_name)

# 创建特征名称到文件路径的映射字典
FEATURE_RASTERS = {}
for band_name, file_path in zip(band_order, sorted_raster_paths):
    FEATURE_RASTERS[band_name] = file_path

# 3) 输出路径
OUT_TIF = r"E:\地上生物量\地上生物量\7,8\2508.tif"

# 4) 分块大小（根据机器内存适当调整）
BLOCK_SIZE = 1024

# 5) 当有 NoData 时的处理策略：True = 任一特征为 NoData 则不预测（输出 NoData）
STRICT_NODATA = True

# 6) 输出 NoData 值
OUTPUT_NODATA = np.nan
# ====================================


def check_and_order_features(artifact, feature_rasters):
    """保证特征名齐全并按训练顺序排序"""
    train_feats = artifact["feature_names"]
    missing = [f for f in train_feats if f not in feature_rasters]
    extra = [f for f in feature_rasters if f not in train_feats]
    
    if missing:
        raise ValueError(f"缺少以下特征栅格: {missing}")
    if extra:
        print(f"[WARN] 发现训练集中未使用的多余特征，将忽略: {extra}")
    
    # 按训练时的特征顺序返回 (特征名, 文件路径) 列表
    ordered = [(f, feature_rasters[f]) for f in train_feats]
    return ordered


def open_rasters(ordered_paths):
    """打开全部特征栅格并进行基本一致性检查"""
    srcs = [rasterio.open(p) for _, p in ordered_paths]
    ref = srcs[0]
    
    for i, src in enumerate(srcs[1:], start=1):
        if src.crs != ref.crs:
            raise ValueError(f"CRS 不一致: {ordered_paths[0][1]} vs {ordered_paths[i][1]}")
        if src.transform != ref.transform:
            raise ValueError(f"仿射变换(分辨率/对齐)不一致: {ordered_paths[0][1]} vs {ordered_paths[i][1]}")
        if src.width != ref.width or src.height != ref.height:
            raise ValueError(f"栅格大小不一致: {ordered_paths[0][1]} vs {ordered_paths[i][1]}")
    
    return srcs


def read_block_as_stack(srcs, window):
    """读取一个 window 的所有波段（特征），返回 shape=(rows, cols, n_features) 以及 nodata mask"""
    arrays = []
    nodata_masks = []
    
    for src in srcs:
        arr = src.read(1, window=window, resampling=Resampling.nearest)  # (rows, cols)
        
        # 处理可能的 NaN 值，将其转换为 NoData
        if src.nodata is not None:
            arr = np.where(np.isnan(arr), src.nodata, arr)
        
        arrays.append(arr)
        ndv = src.nodata
        if ndv is None:
            nodata_masks.append(np.zeros_like(arr, dtype=bool))
        else:
            nodata_masks.append(arr == ndv)
    
    stack = np.stack(arrays, axis=-1)  # (rows, cols, features)
    nodata_any = np.any(np.stack(nodata_masks, axis=-1), axis=-1)  # (rows, cols)
    
    # 额外检查是否还有 NaN 值
    nan_mask = np.any(np.isnan(stack), axis=-1)
    combined_nodata_mask = nodata_any | nan_mask
    
    return stack, combined_nodata_mask


def main():
    # 1) 载入模型
    artifact = joblib.load(MODEL_PATH)
    pipeline = artifact["pipeline"]
    use_log1p = artifact.get("target_log1p", True)

    # 2) 检查并按训练顺序整理特征
    ordered_feats = check_and_order_features(artifact, FEATURE_RASTERS)

    # 3) 打开栅格并做一致性检查
    srcs = open_rasters(ordered_feats)
    ref = srcs[0]

    # 4) 准备输出数据集
    profile = ref.profile.copy()
    profile.update(
        dtype=rasterio.float32,
        count=1,
        compress="LZW",
        nodata=OUTPUT_NODATA,
        BIGTIFF="IF_SAFER"
    )

    h, w = ref.height, ref.width
    out_path = Path(OUT_TIF)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(out_path, "w", **profile) as dst:
        for row_off in range(0, h, BLOCK_SIZE):
            n_rows = min(BLOCK_SIZE, h - row_off)
            for col_off in range(0, w, BLOCK_SIZE):
                n_cols = min(BLOCK_SIZE, w - col_off)
                win = Window(col_off, row_off, n_cols, n_rows)

                stack, nodata_any = read_block_as_stack(srcs, win)  # (r, c, f)
                r, c, f = stack.shape

                # 有效像素掩膜
                valid_mask = ~nodata_any if STRICT_NODATA else np.ones((r, c), dtype=bool)

                if not np.any(valid_mask):
                    out_block = np.full((r, c), OUTPUT_NODATA, dtype=np.float32)
                    dst.write(out_block, 1, window=win)
                    continue

                X_block = stack.reshape(-1, f)  # (r*c, f)
                valid_idx = np.where(valid_mask.reshape(-1))[0]

                # 仅对有效像素做预测
                preds_log = np.full(X_block.shape[0], np.nan, dtype=np.float32)
                try:
                    preds_log[valid_idx] = pipeline.predict(X_block[valid_idx, :]).astype(np.float32)
                except Exception as e:
                    raise RuntimeError(f"预测失败（窗口 row={row_off}, col={col_off}）：{e}")

                # 还原到原尺度
                preds = np.expm1(preds_log) if use_log1p else preds_log

                # 写出（无效像素置 NoData）
                out_block = preds.reshape(r, c)
                out_block[~valid_mask] = OUTPUT_NODATA
                dst.write(out_block.astype(np.float32), 1, window=win)

    # 5) 关闭数据源
    for s in srcs:
        s.close()

    print(f"[OK] AGB 10m 预测完成：{out_path.resolve()}")


if __name__ == "__main__":
    main()