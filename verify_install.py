# verify_install_v2.py
"""改进的验证脚本"""

def verify_installation():
    print("="*70)
    print("验证包安装")
    print("="*70)
    
    packages_to_test = [
        ('numpy', 'import numpy; print(f"  版本: {numpy.__version__}")'),
        ('torch', 'import torch; print(f"  版本: {torch.__version__}")'),
        ('transformers', 'import transformers; print(f"  版本: {transformers.__version__}")'),
        ('huggingface_hub', 'import huggingface_hub; print(f"  版本: {huggingface_hub.__version__}")'),
        ('sentence_transformers', 'import sentence_transformers; print(f"  版本: {sentence_transformers.__version__}"); from sentence_transformers import SentenceTransformer'),
        ('openai', 'import openai; print(f"  版本: {openai.__version__}")'),
        ('faiss', 'import faiss; print("  ✓ faiss可用")'),
        ('datasets', 'import datasets; print(f"  版本: {datasets.__version__}")'),
        ('tiktoken', 'import tiktoken; tiktoken.get_encoding("cl100k_base"); print("  ✓ tiktoken可用")'),
        ('umap', 'import umap; print("  ✓ umap可用")'),
        ('raptor', 'from raptor import RetrievalAugmentation, RetrievalAugmentationConfig; print("  ✓ raptor可导入")'),
    ]
    
    failed = []
    
    for name, test_code in packages_to_test:
        print(f"\n测试 {name}:")
        try:
            exec(test_code)
            print(f"  ✓ {name} 正常")
        except Exception as e:
            print(f"  ❌ {name} 失败: {e}")
            failed.append(name)
    
    print("\n" + "="*70)
    if failed:
        print(f"❌ 失败的包: {', '.join(failed)}")
        print("\n修复建议:")
        if 'sentence_transformers' in failed:
            print("  pip uninstall huggingface_hub -y")
            print("  pip install 'huggingface_hub<0.20.0'")
            print("  pip install sentence-transformers==2.2.2")
        return False
    else:
        print("✓ 所有包安装成功！")
        print("\n可以运行实验:")
        print("  python test_single_paper.py")
        return True

if __name__ == "__main__":
    import sys
    print(f"使用的Python: {sys.executable}\n")
    
    # 显示关键包版本
    print("关键依赖版本检查:")
    try:
        import huggingface_hub
        print(f"  huggingface_hub: {huggingface_hub.__version__}")
    except:
        print("  huggingface_hub: 未安装")
    
    print()
    success = verify_installation()
    sys.exit(0 if success else 1)