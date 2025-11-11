# test_single_paper.py
"""
第一个RAPTOR实验：单篇论文测试

目的：
1. 验证RAPTOR能正常构建树
2. 验证能回答问题
3. 了解整个流程的耗时和成本
"""

import os
import time
from raptor import RetrievalAugmentation, RetrievalAugmentationConfig
from qasper_utils import QasperDataProcessor

def test_single_paper():
    """在单篇论文上测试RAPTOR"""
    
    print("="*70)
    print("RAPTOR单篇论文测试")
    print("="*70)
    
    # 步骤1：检查环境
    print("\n[步骤1] 检查环境配置...")
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 错误：未设置OPENAI_API_KEY")
        print("请运行：export OPENAI_API_KEY='your-key-here'")
        return
    print("✓ API密钥已配置")
    
    # 步骤2：加载数据
    print("\n[步骤2] 加载QASPER数据...")
    processor = QasperDataProcessor("data/qasper/validation.json")
    print(f"✓ 已加载 {len(processor.papers)} 篇论文")
    
    # 选择第一篇论文
    paper_idx = 0
    paper_info = processor.get_paper_info(paper_idx)
    
    print(f"\n选择的论文:")
    print(f"  ID: {paper_info['id']}")
    print(f"  标题: {paper_info['title'][:80]}...")
    print(f"  文本长度: {paper_info['text_length']:,} 字符")
    print(f"  问题数量: {paper_info['num_questions']}")
    
    # 准备数据
    text, qa_pairs = processor.prepare_for_raptor(paper_idx)
    
    # 步骤3：初始化RAPTOR（使用默认配置）
    print("\n[步骤3] 初始化RAPTOR...")
    print("  配置: 默认配置")
    print("  摘要模型: gpt-3.5-turbo")
    print("  QA模型: gpt-3.5-turbo")
    
    config = RetrievalAugmentationConfig()
    RA = RetrievalAugmentation(config=config)
    
    print("✓ RAPTOR已初始化")
    
    # 步骤4：构建RAPTOR树
    print("\n[步骤4] 构建RAPTOR树...")
    print("  这个过程包括:")
    print("  1. 文本分块（chunks）")
    print("  2. 向量嵌入（embeddings）")
    print("  3. 聚类分析（clustering）")
    print("  4. 生成摘要（summarization with GPT-3.5）")
    print("  5. 递归构建多层树结构")
    print("\n  ⏳ 预计耗时: 1-3分钟...")
    print("  💰 预计成本: $0.01-0.05")
    
    start_time = time.time()
    
    try:
        RA.add_documents(text)
        build_time = time.time() - start_time
        
        print(f"\n✓ 树构建完成！")
        print(f"  耗时: {build_time:.1f} 秒")
        
        # 保存树结构
        os.makedirs("trees", exist_ok=True)
        tree_path = f"trees/test_paper_{paper_info['id']}.pkl"
        RA.save(tree_path)
        print(f"  树已保存: {tree_path}")
        
    except Exception as e:
        print(f"\n❌ 构建树时出错: {e}")
        print("\n可能的原因:")
        print("  1. API密钥无效")
        print("  2. 账户余额不足")
        print("  3. 网络连接问题")
        return
    
    # 步骤5：测试问答
    print("\n[步骤5] 测试问答功能...")
    print(f"  共有 {len(qa_pairs)} 个问题，测试前3个\n")
    
    results = []
    
    for i, (question, reference_answers) in enumerate(qa_pairs[:3], 1):
        print(f"\n{'─'*70}")
        print(f"问题 {i}/{min(3, len(qa_pairs))}")
        print(f"{'─'*70}")
        print(f"Q: {question}\n")
        
        # 显示参考答案
        print(f"参考答案 ({len(reference_answers)}个):")
        for j, ref_ans in enumerate(reference_answers, 1):
            print(f"  [{j}] {ref_ans[:100]}...")
        
        # 使用RAPTOR回答
        print(f"\n⏳ RAPTOR正在思考...")
        
        try:
            answer_start = time.time()
            
            # 调用RAPTOR
            answer = RA.answer_question(
                question=question,
                max_tokens=2000,  # 使用2000 tokens的上下文
                collapse_tree=True  # 使用collapsed tree检索
            )
            
            answer_time = time.time() - answer_start
            
            print(f"✓ 回答完成 (耗时: {answer_time:.1f}秒)")
            print(f"\nRAPTOR答案:")
            print(f"  {answer}\n")
            
            results.append({
                'question': question,
                'raptor_answer': answer,
                'reference_answers': reference_answers,
                'time': answer_time
            })
            
        except Exception as e:
            print(f"❌ 回答问题时出错: {e}")
            results.append({
                'question': question,
                'error': str(e)
            })
    
    # 步骤6：总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    
    total_time = time.time() - start_time
    successful_answers = sum(1 for r in results if 'raptor_answer' in r)
    
    print(f"总耗时: {total_time:.1f} 秒")
    print(f"成功回答: {successful_answers}/{len(results)}")
    
    if successful_answers > 0:
        avg_answer_time = sum(r['time'] for r in results if 'time' in r) / successful_answers
        print(f"平均回答时间: {avg_answer_time:.1f} 秒")
    
    print(f"\n树结构已保存，可以重复使用:")
    print(f"  {tree_path}")
    
    print("\n✓ 单篇论文测试完成！")
    print("\n下一步:")
    print("  1. 如果测试成功，可以扩展到多篇论文")
    print("  2. 可以调整参数（max_tokens, top_k等）")
    print("  3. 可以实现评估指标计算")
    
    return results


def test_with_saved_tree():
    """
    测试使用已保存的树回答问题
    （演示如何避免重复构建树）
    """
    
    print("\n" + "="*70)
    print("测试：使用已保存的树")
    print("="*70)
    
    # 查找已保存的树
    import glob
    tree_files = glob.glob("trees/test_paper_*.pkl")
    
    if not tree_files:
        print("❌ 未找到已保存的树文件")
        print("请先运行 test_single_paper() 构建树")
        return
    
    tree_path = tree_files[0]
    print(f"✓ 找到树文件: {tree_path}")
    
    # 加载树
    print("\n加载树...")
    RA = RetrievalAugmentation(tree=tree_path)
    print("✓ 树加载完成（无需重新构建）")
    
    # 回答新问题
    test_questions = [
        "What is the main contribution of this paper?",
        "What datasets were used in the experiments?",
        "What are the limitations mentioned in the paper?"
    ]
    
    print(f"\n测试 {len(test_questions)} 个新问题:\n")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n问题 {i}: {question}")
        
        try:
            answer = RA.answer_question(question, max_tokens=2000)
            print(f"答案: {answer}\n")
        except Exception as e:
            print(f"错误: {e}\n")
    
    print("✓ 已保存树的测试完成！")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("RAPTOR实验 - 第一步")
    print("="*70)
    print("\n本脚本将:")
    print("  1. 在1篇论文上构建RAPTOR树")
    print("  2. 回答3个问题")
    print("  3. 展示完整的工作流程")
    print("\n预计耗时: 2-5分钟")
    print("预计成本: $0.02-0.10")
    print("\n按 Ctrl+C 可随时中断")
    print("="*70)
    
    input("\n按回车键开始测试...")
    
    # 运行单篇论文测试
    results = test_single_paper()
    
    if results:
        # 询问是否测试已保存的树
        print("\n" + "="*70)
        response = input("\n是否测试使用已保存的树？(y/n): ")
        if response.lower() == 'y':
            test_with_saved_tree()