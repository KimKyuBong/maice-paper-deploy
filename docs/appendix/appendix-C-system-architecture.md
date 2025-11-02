# 부록 C. MAICE 시스템 아키텍처 상세

## 시스템 구조 및 기술 스택

---

## 1. 전체 시스템 레이어 구조

```
┌─────────────────────────────────────────────────────────────┐
│                    사용자 인터페이스 계층                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   웹 브라우저  │  │  MathLive   │  │  SSE 스트림   │      │
│  │  (SvelteKit)  │  │  수식 입력   │  │  실시간 응답   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                          ↕ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────┐
│                      백엔드 API 계층                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   FastAPI    │  │ JWT 인증     │  │ Google OAuth │      │
│  │  RESTful API │  │ 세션 관리     │  │   2.0        │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                          ↕ Redis Streams
┌─────────────────────────────────────────────────────────────┐
│                   멀티 에이전트 계층                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ Classifier │  │ Question   │  │  Answer    │            │
│  │   Agent    │  │Improvement │  │ Generator  │            │
│  └────────────┘  └────────────┘  └────────────┘            │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ Observer   │  │   Scorer   │  │  MetaInfo  │            │
│  │   Agent    │  │   Agent    │  │   Agent    │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
                          ↕ PostgreSQL
┌─────────────────────────────────────────────────────────────┐
│                      데이터 저장 계층                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ PostgreSQL   │  │    Redis     │  │   Nginx      │      │
│  │ 대화 세션 DB  │  │  메시지 큐    │  │ 리버스 프록시 │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 주요 기술 스택

[표 C-1] 계층별 기술 스택

| 계층 | 기술 | 버전 | 선택 이유 |
|------|------|------|----------|
| **프론트엔드** | | | |
| - 프레임워크 | SvelteKit | 2.0 | 빠른 반응성, SSR 지원 |
| - 수식 입력 | MathLive | 0.98 | LaTeX 호환, 직관적 UI |
| - 스타일링 | TailwindCSS | 3.4 | 유틸리티 우선, 반응형 |
| - 테마 | Shadcn/ui | - | 일관된 디자인 시스템 |
| **백엔드** | | | |
| - API 서버 | FastAPI | 0.109 | 비동기 처리, 고성능 |
| - 인증 | JWT + OAuth 2.0 | - | 보안, Google 연동 |
| - 검증 | Pydantic | 2.0 | 타입 안전성 |
| **AI 모델** | | | |
| - LLM | GPT-4o-mini | - | 비용 효율, 빠른 응답 |
| - 평가 모델 | Gemini 2.5 Flash | - | 병렬 처리, 루브릭 채점 |
| **데이터베이스** | | | |
| - 메인 DB | PostgreSQL | 16 | 안정성, JSONB 지원 |
| - 메시지 큐 | Redis Streams | 7.2 | 실시간 통신, Pub/Sub |
| - 캐시 | Redis | 7.2 | 세션 관리, 고속 조회 |
| **배포** | | | |
| - 컨테이너 | Docker | 24.0 | 환경 일관성 |
| - 오케스트레이션 | Docker Compose | 2.24 | 다중 서비스 관리 |
| - 웹 서버 | Nginx | 1.25 | 리버스 프록시, SSL |
| **모니터링** | | | |
| - 로그 | Python logging | - | 구조화된 로그 |
| - 데이터 분석 | Pandas | 2.1 | 통계 분석 |

---

## 3. 에이전트 통신 프로토콜

### 3.1 Redis Streams 메시지 구조

```json
{
  "session_id": "sess_20251020_001",
  "user_id": "S042",
  "mode": "agent",
  "message_type": "maice_clarification_question",
  "content": "수학적 귀납법의 어떤 부분이 궁금하신가요?",
  "metadata": {
    "agent_type": "QuestionImprovement",
    "classification": "K2_conceptual",
    "clarification_count": 1,
    "timestamp": "2025-10-20T14:23:15Z"
  }
}
```

---

### 3.2 에이전트 간 협업 메커니즘

```
[학생 질문 입력]
      ↓
┌─────────────────────┐
│ Classifier Agent    │ → K1/K2/K3/K4 분류
└─────────────────────┘
      ↓
┌─────────────────────┐
│QuestionImprovement  │ → 명료화 필요성 판단
│      Agent          │ → 명료화 질문 생성
└─────────────────────┘
      ↓ (명료화 완료)
┌─────────────────────┐
│ AnswerGenerator     │ → 명료화된 질문에 답변
│      Agent          │ → 맞춤형 설명 제공
└─────────────────────┘
      ↓
┌─────────────────────┐
│  Observer Agent     │ → 학습 과정 관찰
│                     │ → 다음 단계 추천
└─────────────────────┘
      ↓
┌─────────────────────┐
│  Scorer Agent       │ → QAC 체크리스트 평가
│                     │ → 질문/답변/맥락 점수
└─────────────────────┘
```

---

## 4. 데이터베이스 스키마

### 4.1 주요 테이블 구조

**sessions 테이블**:
```sql
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    mode VARCHAR(20) CHECK (mode IN ('agent', 'freepass')),
    current_stage VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);
```

**messages 테이블**:
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(id),
    role VARCHAR(20),
    message_type VARCHAR(50),
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**evaluations 테이블** (QAC 점수):
```sql
CREATE TABLE evaluations (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(id),
    question_score FLOAT,
    answer_score FLOAT,
    context_score FLOAT,
    total_score FLOAT,
    checklist JSONB,
    evaluated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 5. 배포 인프라 구성

### 5.1 Docker Compose 구조

```yaml
version: '3.8'

services:
  frontend:
    image: maice-frontend:latest
    ports:
      - "3000:3000"
    depends_on:
      - backend
  
  backend:
    image: maice-backend:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://...
    depends_on:
      - postgres
      - redis
  
  agents:
    image: maice-agents:latest
    deploy:
      replicas: 8  # 8개 에이전트 프로세스
    depends_on:
      - redis
      - postgres
  
  postgres:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7.2
    volumes:
      - redis_data:/data
  
  nginx:
    image: nginx:1.25
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - frontend
      - backend
```

---

### 5.2 Blue-Green 무중단 배포

```
┌─────────────┐
│   Nginx     │
│ Load        │
│ Balancer    │
└─────────────┘
    ↓      ↓
┌─────┐  ┌─────┐
│Blue │  │Green│
│(구버전)│  │(신버전)│
└─────┘  └─────┘

배포 프로세스:
1. Green 환경에 신버전 배포
2. 헬스 체크 확인
3. Nginx 트래픽을 Green으로 전환
4. Blue 환경 종료
```

---

## 6. 성능 지표

[표 C-2] 시스템 성능 측정 결과

| 지표 | 값 | 목표 | 달성 여부 |
|------|-----|------|----------|
| API 평균 응답 시간 | 2.3초 | <3초 | ✅ |
| 에이전트 평균 응답 | 2-42초 | <60초 | ✅ |
| 동시 세션 처리 | 50개 | >30개 | ✅ |
| 데이터베이스 쿼리 | 15ms | <50ms | ✅ |
| 세션 저장 성공률 | 99.8% | >99% | ✅ |
| 시스템 가동률 | 99.2% | >99% | ✅ |

---

## 7. 보안 및 개인정보 보호

**인증 체계**:
- JWT 토큰 기반 인증
- Google OAuth 2.0 연동
- 세션 만료 시간: 24시간

**데이터 보호**:
- 개인식별정보 암호화 (AES-256)
- HTTPS 통신 (SSL/TLS 1.3)
- 데이터베이스 접근 제한 (IP whitelist)

**로그 관리**:
- 개인정보는 로그에 기록하지 않음
- 세션 ID로만 추적
- 로그 보관 기간: 3개월

---

## 8. 에이전트별 역할 상세

[표 C-3] 에이전트 역할 및 프롬프트 전략

| 에이전트 | 역할 | 프롬프트 전략 | 평균 응답 시간 |
|----------|------|-------------|--------------|
| **Classifier** | 질문 유형 분류 | K1-K4 분류 기준 제공 | 2초 |
| **QuestionImprovement** | 명료화 질문 생성 | Dewey 5단계 기반 | 8초 |
| **AnswerGenerator** | 답변 생성 | 단계별 설명 구조 | 15초 |
| **Observer** | 학습 과정 관찰 | 메타인지 유도 질문 | 5초 |
| **Scorer** | 품질 평가 | QAC 체크리스트 기준 | 12초 |
| **MetaInfo** | 단원 정보 제공 | 수학적 귀납법 특화 | 3초 |

---

## 9. 확장성 및 유지보수

**수평적 확장**:
- 에이전트 프로세스 수 조절 가능 (현재 8개)
- Redis를 통한 분산 처리
- 로드 밸런서를 통한 트래픽 분산

**모니터링**:
- 에이전트별 처리 속도 추적
- 오류율 실시간 모니터링
- 세션 통계 대시보드

**업데이트 전략**:
- Blue-Green 배포로 무중단 업데이트
- 롤백 기능 (30초 내 이전 버전 복구)
- 자동 재시작 (Docker restart policy)

---

본 아키텍처는 실제 고등학교 환경에서 179개 세션을 안정적으로 처리하며, 확장 가능하고 유지보수가 용이한 시스템임을 입증하였다.

