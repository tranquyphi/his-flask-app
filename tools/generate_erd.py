#!/usr/bin/env python3
"""
Generate ERD diagram file from DDL
Supports multiple output formats: .dot, .mermaid, .dbml
"""

import re
import sys
from pathlib import Path

def parse_ddl_to_dot(ddl_file):
    """Parse DDL and generate Graphviz .dot file"""
    
    with open(ddl_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract tables and their columns
    tables = {}
    foreign_keys = []
    
    # Find CREATE TABLE statements
    table_pattern = r'CREATE TABLE `(\w+)` \((.*?)\);'
    matches = re.findall(table_pattern, content, re.DOTALL | re.IGNORECASE)
    
    for table_name, table_def in matches:
        columns = []
        
        # Parse columns
        lines = table_def.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('`') and 'COMMENT' in line:
                col_match = re.match(r'`(\w+)`\s+(\w+(?:\(\d+\))?)', line)
                if col_match:
                    col_name, col_type = col_match.groups()
                    is_pk = 'PRIMARY KEY' in line
                    columns.append({
                        'name': col_name,
                        'type': col_type,
                        'is_pk': is_pk
                    })
        
        tables[table_name] = columns
    
    # Find foreign key relationships
    fk_pattern = r'ADD FOREIGN KEY \((\w+)\) REFERENCES (\w+)\((\w+)\)'
    fk_matches = re.findall(fk_pattern, content, re.IGNORECASE)
    
    # Generate DOT content
    dot_content = """digraph hospital_erd {
    rankdir=TB;
    node [shape=record, style=filled, fillcolor=lightblue];
    edge [color=gray];
    
"""
    
    # Add tables
    for table_name, columns in tables.items():
        dot_content += f'    {table_name} [label="'
        dot_content += f'{{<table>{table_name}|'
        
        for col in columns:
            pk_marker = ' 🔑' if col['is_pk'] else ''
            dot_content += f'{col["name"]} : {col["type"]}{pk_marker}\\l'
        
        dot_content += '}"];\n'
    
    dot_content += '\n    // Relationships\n'
    
    # Add relationships
    for fk_col, ref_table, ref_col in fk_matches:
        # Find the table containing this foreign key
        for table_name, columns in tables.items():
            if any(col['name'] == fk_col for col in columns):
                dot_content += f'    {table_name} -> {ref_table} [label="{fk_col}"];\n'
                break
    
    dot_content += '}\n'
    
    return dot_content

def parse_ddl_to_mermaid(ddl_file):
    """Parse DDL and generate Mermaid ERD"""
    
    with open(ddl_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    mermaid_content = """erDiagram
"""
    
    # Extract tables and relationships
    table_pattern = r'CREATE TABLE `(\w+)` \((.*?)\);'
    matches = re.findall(table_pattern, content, re.DOTALL | re.IGNORECASE)
    
    for table_name, table_def in matches:
        mermaid_content += f'    {table_name} {{\n'
        
        lines = table_def.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('`') and 'COMMENT' in line:
                col_match = re.match(r'`(\w+)`\s+(\w+(?:\(\d+\))?)', line)
                if col_match:
                    col_name, col_type = col_match.groups()
                    is_pk = 'PRIMARY KEY' in line
                    pk_marker = ' PK' if is_pk else ''
                    mermaid_content += f'        {col_type} {col_name}{pk_marker}\n'
        
        mermaid_content += '    }\n\n'
    
    # Add relationships
    fk_pattern = r'ADD FOREIGN KEY \((\w+)\) REFERENCES (\w+)\((\w+)\)'
    fk_matches = re.findall(fk_pattern, content, re.IGNORECASE)
    
    # Find table relationships
    tables = [match[0] for match in matches]
    processed_relationships = set()
    
    for fk_col, ref_table, ref_col in fk_matches:
        for table_name in tables:
            table_content = re.search(rf'CREATE TABLE `{table_name}` \((.*?)\);', content, re.DOTALL)
            if table_content and fk_col in table_content.group(1):
                rel_key = f"{table_name}-{ref_table}"
                if rel_key not in processed_relationships:
                    mermaid_content += f'    {table_name} ||--o{{ {ref_table} : has\n'
                    processed_relationships.add(rel_key)
                break
    
    return mermaid_content

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 generate_erd.py <ddl_file>")
        sys.exit(1)
    
    ddl_file = sys.argv[1]
    if not Path(ddl_file).exists():
        print(f"Error: File {ddl_file} not found")
        sys.exit(1)
    
    base_name = Path(ddl_file).stem
    
    # Generate DOT file
    try:
        dot_content = parse_ddl_to_dot(ddl_file)
        dot_file = f"{base_name}.dot"
        with open(dot_file, 'w', encoding='utf-8') as f:
            f.write(dot_content)
        print(f"✅ Generated: {dot_file}")
        print(f"   Convert to image: dot -Tpng {dot_file} -o {base_name}.png")
    except Exception as e:
        print(f"❌ Error generating DOT file: {e}")
    
    # Generate Mermaid file
    try:
        mermaid_content = parse_ddl_to_mermaid(ddl_file)
        mermaid_file = f"{base_name}.mmd"
        with open(mermaid_file, 'w', encoding='utf-8') as f:
            f.write(mermaid_content)
        print(f"✅ Generated: {mermaid_file}")
        print(f"   View online: https://mermaid.live/")
    except Exception as e:
        print(f"❌ Error generating Mermaid file: {e}")

if __name__ == "__main__":
    main()
