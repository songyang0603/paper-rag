# qasper_utils.py
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class QasperDataProcessor:
    """
    QASPER数据集处理工具（健壮版）
    """
    
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.papers = []
        self.paper_ids = []
        self.load_data()
    
    def load_data(self):
        """加载QASPER数据"""
        print(f"加载数据: {self.data_path}")
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {self.data_path}")
        
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 将字典转换为列表
            for paper_id, paper_data in data.items():
                paper_data['id'] = paper_id
                self.papers.append(paper_data)
                self.paper_ids.append(paper_id)
            
            print(f"✓ 已加载 {len(self.papers)} 篇论文")
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析错误: {e}")
            raise
        except Exception as e:
            print(f"❌ 加载数据失败: {e}")
            raise
    
    def get_paper_text(self, paper: Dict) -> str:
        """
        提取论文全文（健壮版）
        """
        full_text_parts = []
        
        try:
            # 添加标题
            title = paper.get('title', 'Untitled')
            if title:
                full_text_parts.append(f"# {title}\n")
            
            # 添加摘要
            abstract = paper.get('abstract', '')
            if abstract:
                full_text_parts.append(f"## Abstract\n{abstract}\n")
            
            # 添加全文
            full_text_parts.append("## Full Text\n")
            
            # 处理full_text
            full_text = paper.get('full_text', [])
            
            for section in full_text:
                if not isinstance(section, dict):
                    continue
                
                # 安全地获取section_name
                section_name = section.get('section_name')
                if section_name is None:
                    section_name = ''
                
                paragraphs = section.get('paragraphs', [])
                
                # 添加section名称
                if section_name and str(section_name).strip():
                    full_text_parts.append(f"\n### {str(section_name).strip()}\n")
                
                # 添加段落
                for para in paragraphs:
                    if para is not None and str(para).strip():
                        full_text_parts.append(f"{str(para).strip()}\n")
            
            return "\n".join(full_text_parts)
            
        except Exception as e:
            print(f"⚠️  提取论文文本时出错 (ID: {paper.get('id', 'unknown')}): {e}")
            # 返回最小可用文本
            return f"# {paper.get('title', 'Error')}\n\n{paper.get('abstract', 'Error loading text')}"
    
    def get_questions_and_answers(self, paper: Dict) -> List[Tuple[str, List[Dict]]]:
        """提取问题和答案"""
        qa_pairs = []
        
        try:
            qas = paper.get('qas', [])
            
            for qa in qas:
                if not isinstance(qa, dict):
                    continue
                
                question = qa.get('question', '')
                answers = qa.get('answers', [])
                
                if question:  # 只保留有问题的条目
                    qa_pairs.append((question, answers))
            
        except Exception as e:
            print(f"⚠️  提取问答对时出错 (ID: {paper.get('id', 'unknown')}): {e}")
        
        return qa_pairs
    
    def extract_answer_text(self, answer_dict: Dict) -> Optional[str]:
        """从答案字典中提取文本"""
        try:
            answer = answer_dict.get('answer', {})
            
            if not answer:
                return None
            
            # 1. 自由文本答案
            if 'free_form_answer' in answer and answer['free_form_answer']:
                return str(answer['free_form_answer'])
            
            # 2. 提取式答案
            if 'extractive_spans' in answer and answer['extractive_spans']:
                spans = answer['extractive_spans']
                if isinstance(spans, list):
                    return ' '.join(str(s) for s in spans if s)
            
            # 3. 是非题
            if 'yes_no' in answer:
                return 'Yes' if answer['yes_no'] else 'No'
            
            # 4. 无法回答
            if 'unanswerable' in answer and answer['unanswerable']:
                return 'Unanswerable'
            
            return None
            
        except Exception as e:
            print(f"⚠️  提取答案文本时出错: {e}")
            return None
    
    def prepare_for_raptor(self, paper_index: int) -> Tuple[str, List[Tuple[str, List[str]]]]:
        """
        为RAPTOR准备数据（健壮版）
        """
        if paper_index < 0 or paper_index >= len(self.papers):
            raise IndexError(f"论文索引超出范围: {paper_index} (总数: {len(self.papers)})")
        
        paper = self.papers[paper_index]
        
        # 获取论文文本
        text = self.get_paper_text(paper)
        
        # 获取问答对
        raw_qa_pairs = self.get_questions_and_answers(paper)
        
        # 处理答案文本
        processed_qa_pairs = []
        for question, answers in raw_qa_pairs:
            answer_texts = []
            
            for ans in answers:
                if not isinstance(ans, dict):
                    continue
                
                ans_text = self.extract_answer_text(ans)
                if ans_text and ans_text != 'Unanswerable':
                    answer_texts.append(ans_text)
            
            if answer_texts:
                processed_qa_pairs.append((question, answer_texts))
        
        return text, processed_qa_pairs
    
    def get_paper_info(self, paper_index: int) -> Dict:
        """获取论文的基本信息"""
        try:
            paper = self.papers[paper_index]
            text, qa_pairs = self.prepare_for_raptor(paper_index)
            
            # 安全地计算段落数
            num_paragraphs = 0
            full_text = paper.get('full_text', [])
            for section in full_text:
                if isinstance(section, dict):
                    paragraphs = section.get('paragraphs', [])
                    if isinstance(paragraphs, list):
                        num_paragraphs += len(paragraphs)
            
            title = paper.get('title', 'Untitled')
            abstract = paper.get('abstract', '')
            
            return {
                'id': paper.get('id', 'unknown'),
                'title': (title[:80] + '...') if len(title) > 80 else title,
                'abstract': (abstract[:200] + '...') if len(abstract) > 200 else abstract,
                'text_length': len(text),
                'text_length_readable': f"{len(text):,} 字符",
                'num_questions': len(qa_pairs),
                'num_paragraphs': num_paragraphs,
                'num_sections': len(full_text)
            }
            
        except Exception as e:
            return {
                'id': paper.get('id', 'unknown') if paper_index < len(self.papers) else 'invalid_index',
                'error': f"获取信息失败: {str(e)}"
            }
    
    def print_statistics(self):
        """打印数据集统计信息"""
        print("\n" + "="*60)
        print("数据集统计:")
        print("="*60)
        
        total_questions = 0
        answerable_questions = 0
        errors = 0
        
        for i in range(len(self.papers)):
            try:
                raw_qa = self.get_questions_and_answers(self.papers[i])
                total_questions += len(raw_qa)
                
                _, qa_pairs = self.prepare_for_raptor(i)
                answerable_questions += len(qa_pairs)
                
            except Exception as e:
                errors += 1
                print(f"⚠️  处理论文 {i} 时出错: {e}")
        
        avg_questions = total_questions / len(self.papers) if self.papers else 0
        
        print(f"论文总数: {len(self.papers)}")
        print(f"问题总数: {total_questions}")
        print(f"可回答问题数: {answerable_questions}")
        print(f"平均每篇论文问题数: {avg_questions:.2f}")
        
        if total_questions > 0:
            print(f"可回答率: {answerable_questions/total_questions*100:.1f}%")
        
        if errors > 0:
            print(f"⚠️  处理错误数: {errors}")
        
        print("="*60)


def test_data_processor():
    """测试数据处理器"""
    print("\n" + "="*60)
    print("测试QASPER数据处理器")
    print("="*60)
    
    # 加载验证集
    try:
        processor = QasperDataProcessor("data/qasper/validation.json")
    except Exception as e:
        print(f"❌ 加载数据失败: {e}")
        return False
    
    # 打印统计信息
    try:
        processor.print_statistics()
    except Exception as e:
        print(f"❌ 统计信息失败: {e}")
        return False
    
    # 测试第一篇论文
    print("\n" + "="*60)
    print("第一篇论文详细信息:")
    print("="*60)
    
    try:
        info = processor.get_paper_info(0)
        
        if 'error' in info:
            print(f"⚠️  {info['error']}")
        else:
            for key, value in info.items():
                print(f"  {key:20s}: {value}")
    except Exception as e:
        print(f"❌ 获取论文信息失败: {e}")
        return False
    
    # 测试数据准备
    print("\n" + "="*60)
    print("测试RAPTOR数据准备:")
    print("="*60)
    
    try:
        text, qa_pairs = processor.prepare_for_raptor(0)
        
        print(f"✓ 论文文本长度: {len(text):,} 字符")
        print(f"✓ 可回答问题数量: {len(qa_pairs)}")
        
        # 显示文本开头
        if text:
            preview = text[:200].replace('\n', ' ')
            print(f"\n论文文本开头:")
            print(f"  {preview}...")
        
        # 显示第一个问题
        if qa_pairs:
            q, answers = qa_pairs[0]
            print(f"\n第一个问题:")
            print(f"  问题: {q[:100]}...")
            print(f"  参考答案数量: {len(answers)}")
            for i, ans in enumerate(answers[:2], 1):
                ans_preview = ans[:80] + '...' if len(ans) > 80 else ans
                print(f"  答案{i}: {ans_preview}")
        
        print("\n" + "="*60)
        print("✓ 数据处理器测试通过！")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ 数据准备失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_data_processor()
    
    if success:
        print("\n✅ 所有测试通过，可以继续下一步！")
        print("\n下一步：")
        print("  1. 确认OpenAI API密钥已设置")
        print("  2. 运行第一个RAPTOR实验")
    else:
        print("\n❌ 测试失败，请检查错误信息")