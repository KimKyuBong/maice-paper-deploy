#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psycopg2
import json

try:
    # PostgreSQL 연결
    conn = psycopg2.connect(
        host='192.168.1.110',
        database='maice_agent',
        user='postgres',
        password='postgres',
        port=5432,
        connect_timeout=5
    )
    
    cur = conn.cursor()
    
    # 모든 테이블 확인
    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    all_tables = cur.fetchall()
    print('=== All tables in maice_agent database ===')
    for table in all_tables:
        print(f'  - {table[0]}')
    
    # prompts 테이블이 있는지 확인
    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name LIKE '%prompt%'
    """)
    prompt_tables = cur.fetchall()
    print('\n=== Prompt related tables ===')
    for table in prompt_tables:
        print(f'  - {table[0]}')
    
    # agents 테이블 확인
    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name LIKE '%agent%'
    """)
    agent_tables = cur.fetchall()
    print('\n=== Agent related tables ===')
    for table in agent_tables:
        print(f'  - {table[0]}')
    
    # 세션 테이블 확인
    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name LIKE '%session%'
    """)
    session_tables = cur.fetchall()
    print('\n=== Session related tables ===')
    for table in session_tables:
        print(f'  - {table[0]}')
    
    conn.close()
    print('\n✅ Database connection successful!')
    
except Exception as e:
    print(f'❌ Error: {e}')

