#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psycopg2
import json
from collections import Counter

try:
    conn = psycopg2.connect(
        host='192.168.1.110',
        database='maice_agent',
        user='postgres',
        password='postgres',
        port=5432,
        connect_timeout=10
    )
    
    cur = conn.cursor()
    
    # llm_prompt_logs 테이블 구조 확인
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'llm_prompt_logs'
        ORDER BY ordinal_position
    """)
    columns = cur.fetchall()
    print('=== llm_prompt_logs table structure ===')
    for col in columns:
        print(f'  {col[0]}: {col[1]}')
    
    # agent_name별 프롬프트 개수 확인
    cur.execute("""
        SELECT 
            agent_name,
            COUNT(*) as count
        FROM llm_prompt_logs
        GROUP BY agent_name
        ORDER BY count DESC
    """)
    agent_counts = cur.fetchall()
    print('\n=== Agent type counts ===')
    for agent, count in agent_counts:
        print(f'  {agent}: {count}')
    
    # 각 에이전트별로 프롬프트 1개씩 샘플 가져오기
    print('\n=== Sample prompts by agent type ===\n')
    
    for agent_name, _ in agent_counts:
        cur.execute("""
            SELECT 
                input_prompt,
                created_at
            FROM llm_prompt_logs
            WHERE agent_name = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (agent_name,))
        
        result = cur.fetchone()
        if result:
            input_prompt, created_at = result
            print(f'{"="*80}')
            print(f'Agent: {agent_name}')
            print(f'Date: {created_at}')
            print(f'{"="*80}')
            print(f'\n[Input Prompt]')
            print(input_prompt[:800] if input_prompt else 'None')
            if input_prompt and len(input_prompt) > 800:
                print(f'... (total {len(input_prompt)} chars)')
            print('\n')
    
    # 프롬프트를 파일로 저장
    output = {}
    for agent_name, _ in agent_counts:
        cur.execute("""
            SELECT 
                input_prompt
            FROM llm_prompt_logs
            WHERE agent_name = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (agent_name,))
        
        result = cur.fetchone()
        if result:
            input_prompt = result[0]
            output[agent_name] = {
                'prompt': input_prompt
            }
    
    with open('../../analysis/newtest/actual_prompts_from_db.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f'✅ Prompts saved to actual_prompts_from_db.json')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()

