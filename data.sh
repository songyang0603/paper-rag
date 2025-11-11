#!/bin/bash
# download_qasper_from_s3.sh - 从AWS S3直接下载QASPER数据

echo "=========================================="
echo "从AWS S3下载QASPER数据集"
echo "=========================================="

# 创建临时下载目录
mkdir -p data/qasper_temp
cd data/qasper_temp

# 下载训练集和验证集（打包在一起）
echo ""
echo "1. 下载训练集和验证集..."
curl -L "https://qasper-dataset.s3.us-west-2.amazonaws.com/qasper-train-dev-v0.3.tgz" -o train-dev.tgz

# 下载测试集
echo ""
echo "2. 下载测试集..."
curl -L "https://qasper-dataset.s3.us-west-2.amazonaws.com/qasper-test-and-evaluator-v0.3.tgz" -o test.tgz

# 解压文件
echo ""
echo "3. 解压文件..."
tar -xzf train-dev.tgz
tar -xzf test.tgz

# 移动JSON文件到正确位置
echo ""
echo "4. 整理文件..."
cd ..
mkdir -p qasper

# 移动文件（文件名根据解压后的实际情况可能需要调整）
if [ -f "qasper_temp/qasper-train-v0.3.json" ]; then
    mv qasper_temp/qasper-train-v0.3.json qasper/train.json
    echo "  ✓ 训练集已移动"
fi

if [ -f "qasper_temp/qasper-dev-v0.3.json" ]; then
    mv qasper_temp/qasper-dev-v0.3.json qasper/validation.json
    echo "  ✓ 验证集已移动"
fi

if [ -f "qasper_temp/qasper-test-v0.3.json" ]; then
    mv qasper_temp/qasper-test-v0.3.json qasper/test.json
    echo "  ✓ 测试集已移动"
fi

# 清理临时文件
echo ""
echo "5. 清理临时文件..."
rm -rf qasper_temp

cd ..

# 显示结果
echo ""
echo "=========================================="
echo "下载完成！"
echo "=========================================="
ls -lh qasper/

# 验证文件
echo ""
echo "文件验证:"
for file in qasper/*.json; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        lines=$(wc -l < "$file" 2>/dev/null || echo "无法计算")
        echo "  $(basename $file): $size, $lines 行"
    fi
done