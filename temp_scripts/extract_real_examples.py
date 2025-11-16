#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""실제 세션 데이터에서 예시 추출"""

import json
import sys
import os

# 파일 경로
session_file = "analysis/newtest/학생세션_수집_20251105_154459.json"

try:
    with open(session_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ 총 세션 수: {data['counts']['sessions']}")
    print(f"✅ 총 학생 수: {data['counts']['students']}")
    print(f"✅ 총 메시지 수: {data['counts']['messages']}")
    print()
    
    # 세션 찾기
    sessions = data.get('sessions', [])
    print(f"세션 데이터 구조 확인...")
    if sessions:
        print(f"첫 번째 세션 키: {list(sessions[0].keys())}")
        print()
        
        # Agent 모드 세션 찾기
        agent_sessions = [s for s in sessions if s.get('user_mode') == 'agent']
        freepass_sessions = [s for s in sessions if s.get('user_mode') == 'freepass']
        
        print(f"Agent 세션: {len(agent_sessions)}개")
        print(f"Freepass 세션: {len(freepass_sessions)}개")
        print()
        
        # 대화가 있는 세션 찾기
        conv_sessions = [s for s in sessions if s.get('conversation_history')]
        print(f"대화 있는 세션: {len(conv_sessions)}개")
        
        if conv_sessions:
            # 첫 번째 대화 예시
            first = conv_sessions[0]
            print("\n=== 첫 번째 대화 세션 예시 ===")
            print(f"세션 ID: {first.get('id')}")
            print(f"모드: {first.get('user_mode')}")
            print(f"제목: {first.get('title', 'N/A')}")
            print(f"대화 길이: {len(first.get('conversation_history', []))}턴")
            
            # 대화 내용 출력 (처음 3턴)
            conv = first.get('conversation_history', [])
            for i, turn in enumerate(conv[:3]):
                print(f"\n[Turn {i+1}]")
                print(f"Role: {turn.get('role')}")
                content = turn.get('content', '')
                print(f"Content: {content[:200]}...")
        
        # K1, K2, K3, K4 예시 찾기
        print("\n\n=== K1-K4 질문 유형별 실제 예시 찾기 ===")
        
        # 분류 정보가 있는 세션 찾기
        classified_sessions = []
        for s in sessions:
            conv = s.get('conversation_history', [])
            for turn in conv:
                if turn.get('role') == 'assistant' and 'knowledge_code' in turn.get('content', ''):
                    classified_sessions.append(s)
                    break
        
        print(f"분류 정보 포함 세션: {len(classified_sessions)}개")
        
except FileNotFoundError:
    print(f"❌ 파일을 찾을 수 없습니다: {session_file}")
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()


