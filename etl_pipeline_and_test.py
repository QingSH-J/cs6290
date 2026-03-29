import pandas as pd
import os

def run_data_quality_tests(df):
    """
    数据工程师的核心价值：数据质量测试 (Data Quality Assurance)
    """
    print("\n🧪 开始执行数据质量自动化测试...")
    
    # 测试 1: 检查是否有缺失值 (NaN)
    missing_values = df.isnull().sum().sum()
    assert missing_values == 0, f"❌ 测试失败: 数据集中存在 {missing_values} 个缺失值！"
    print("   ✅ 测试 1 通过: 无缺失值 (No NaN values)")
    
    # 测试 2: 检查日期是否严格按时间顺序排列 (没有乱序)
    is_sorted = df['date'].is_monotonic_increasing
    assert is_sorted, "❌ 测试失败: 日期没有按时间顺序排列！"
    print("   ✅ 测试 2 通过: 时间序列顺序正确 (Chronological order verified)")
    
    # 测试 3: 检查计算的收益率和波动率是否在合理范围内
    # 比如：收益率不应该出现无穷大 (inf)
    assert not df.isin([float('inf'), float('-inf')]).any().any(), "❌ 测试失败: 数据中存在无穷大值！"
    print("   ✅ 测试 3 通过: 衍生特征数据边界正常 (No infinite values)")

    print("🎉 所有数据质量测试通过！数据集达到了交付标准 (Production Ready)。")

def finalize_pipeline(input_file, final_output_file):
    print(f"🔄 [ETL 阶段] 读取 M2 特征数据: {input_file}...")
    
    try:
        # 模拟流水线最后的加载和格式化过程
        df = pd.read_csv(input_file)
        df['date'] = pd.to_datetime(df['date'])
        
        # 运行严格的测试
        run_data_quality_tests(df)
        
        # 最终交付物保存
        df.to_csv(final_output_file, index=False)
        print(f"\n📦 [交接准备] 最终交付文件已生成: {final_output_file}")
        print("   👉 请通知 '可视化与验证师' 使用此文件进行绘图。")
        
    except AssertionError as ae:
        print(ae)
    except Exception as e:
        print(f"❌ 管道运行错误: {e}")

if __name__ == "__main__":
    # 使用你 M2 生成的特征文件
    INPUT_FILE = "trump_2024_features_m2.csv" 
    FINAL_OUTPUT = "FINAL_trump_2024_ready_for_viz.csv"
    
    finalize_pipeline(INPUT_FILE, FINAL_OUTPUT)