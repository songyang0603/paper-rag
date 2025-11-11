# inspect_tree.py
"""
详细检查和可视化RAPTOR树结构
"""

import pickle
import json
from pathlib import Path
from collections import defaultdict

def load_tree(tree_path):
    """加载树文件"""
    with open(tree_path, 'rb') as f:
        tree = pickle.load(f)
    return tree


def analyze_tree_structure(tree):
    """分析树的结构"""
    
    print("="*80)
    print("RAPTOR树结构分析")
    print("="*80)
    
    # 1. 基本统计
    print("\n【1. 基本统计】")
    print(f"  总节点数: {len(tree.all_nodes)}")
    print(f"  树层数: {tree.num_layers + 1}")  # 包含layer 0
    print(f"  叶子节点数: {len(tree.leaf_nodes)}")
    print(f"  根节点数: {len(tree.root_nodes)}")
    
    # 2. 各层分布
    print("\n【2. 各层节点分布】")
    for layer_idx, nodes in tree.layer_to_nodes.items():
        print(f"  Layer {layer_idx}: {len(nodes)} 个节点")
        
        # 计算该层的总文本量
        total_chars = sum(len(node.text) for node in nodes)
        avg_chars = total_chars / len(nodes) if nodes else 0
        print(f"    - 总字符数: {total_chars:,}")
        print(f"    - 平均字符数: {avg_chars:.0f}")
    
    # 3. 树的形状
    print("\n【3. 树的形状（父子关系）】")
    for layer_idx in range(tree.num_layers):
        if layer_idx in tree.layer_to_nodes:
            current_layer = tree.layer_to_nodes[layer_idx]
            
            children_counts = []
            for node in current_layer:
                children_counts.append(len(node.children))
            
            if children_counts:
                avg_children = sum(children_counts) / len(children_counts)
                print(f"  Layer {layer_idx} → Layer {layer_idx + 1}")
                print(f"    - 平均子节点数: {avg_children:.1f}")
                print(f"    - 子节点数范围: {min(children_counts)} - {max(children_counts)}")
    
    return tree


def show_sample_nodes(tree, num_samples=2):
    """展示样例节点"""
    
    print("\n" + "="*80)
    print("样例节点内容")
    print("="*80)
    
    # 叶子节点样例
    print("\n【叶子节点样例（原始文本块）】")
    leaf_nodes = list(tree.leaf_nodes.values())
    for i, node in enumerate(leaf_nodes[:num_samples], 1):
        print(f"\n  叶子节点 {i} (索引 {node.index}):")
        print(f"  ├─ 文本长度: {len(node.text)} 字符")
        print(f"  ├─ 子节点数: {len(node.children)}")
        print(f"  └─ 内容预览:")
        print(f"     {node.text[:200]}...")
    
    # 父节点样例（摘要）
    if tree.num_layers > 0:
        print("\n【父节点样例（摘要）】")
        layer_1_nodes = tree.layer_to_nodes[1]
        for i, node in enumerate(layer_1_nodes[:num_samples], 1):
            print(f"\n  父节点 {i} (索引 {node.index}):")
            print(f"  ├─ 文本长度: {len(node.text)} 字符")
            print(f"  ├─ 子节点数: {len(node.children)}")
            print(f"  ├─ 子节点索引: {sorted(list(node.children))}")
            print(f"  └─ 摘要内容:")
            print(f"     {node.text}")


def extract_tree_to_json(tree, output_path):
    """将树导出为JSON格式（便于查看）"""
    
    tree_dict = {
        'meta': {
            'total_nodes': len(tree.all_nodes),
            'num_layers': tree.num_layers + 1,
            'leaf_nodes': len(tree.leaf_nodes),
            'root_nodes': len(tree.root_nodes)
        },
        'layers': {}
    }
    
    # 导出每一层
    for layer_idx, nodes in tree.layer_to_nodes.items():
        layer_data = []
        for node in nodes:
            node_data = {
                'index': node.index,
                'text': node.text,
                'text_length': len(node.text),
                'num_children': len(node.children),
                'children': sorted(list(node.children))
            }
            layer_data.append(node_data)
        
        tree_dict['layers'][f'layer_{layer_idx}'] = layer_data
    
    # 保存为JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(tree_dict, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ 树结构已导出为JSON: {output_path}")
    print(f"  可以用文本编辑器打开查看")


def visualize_tree_graph(tree, output_path='tree_structure.txt'):
    """生成ASCII艺术风格的树结构可视化"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("RAPTOR树结构可视化\n")
        f.write("="*80 + "\n\n")
        
        # 从根节点开始
        for layer_idx in range(tree.num_layers, -1, -1):
            f.write(f"\n{'─'*80}\n")
            f.write(f"Layer {layer_idx}\n")
            f.write(f"{'─'*80}\n\n")
            
            nodes = tree.layer_to_nodes[layer_idx]
            
            for i, node in enumerate(nodes):
                # 节点信息
                f.write(f"Node {node.index}:\n")
                f.write(f"  文本: {node.text[:100]}...\n")
                f.write(f"  长度: {len(node.text)} 字符\n")
                
                # 子节点
                if node.children:
                    f.write(f"  子节点: {sorted(list(node.children))}\n")
                
                f.write("\n")
    
    print(f"\n✓ 树结构可视化已保存: {output_path}")


def main():
    """主函数"""
    
    # 找到树文件
    tree_files = list(Path("trees").glob("*.pkl"))
    
    if not tree_files:
        print("❌ 未找到树文件")
        return
    
    tree_path = tree_files[0]
    print(f"分析树文件: {tree_path}\n")
    
    # 加载树
    tree = load_tree(tree_path)
    
    # 1. 结构分析
    analyze_tree_structure(tree)
    
    # 2. 样例节点
    show_sample_nodes(tree, num_samples=3)
    
    # 3. 导出JSON
    json_path = str(tree_path).replace('.pkl', '.json')
    extract_tree_to_json(tree, json_path)
    
    # 4. 生成可视化
    viz_path = str(tree_path).replace('.pkl', '_structure.txt')
    visualize_tree_graph(tree, viz_path)
    
    print("\n" + "="*80)
    print("分析完成！")
    print("="*80)
    print("\n生成的文件:")
    print(f"  1. {json_path} - JSON格式（可用文本编辑器打开）")
    print(f"  2. {viz_path} - ASCII可视化")
    print("\n提示:")
    print("  - 用VS Code或任何文本编辑器打开JSON文件")
    print("  - JSON文件包含完整的树结构和所有节点内容")


if __name__ == "__main__":
    main()