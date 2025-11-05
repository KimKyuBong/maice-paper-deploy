# Abstract (English)

## Design and Development of an AI Agent Supporting Question Clarification in Mathematics Learning: Focusing on Mathematical Induction for High School Grade 2

By Hwang Si-hyun  
Major in AI Convergence Education  
Graduate School of Education, Pusan National University  
Supervised by Professor [Name]

---

## Abstract

### Background

Despite the rapid adoption of generative AI tools like ChatGPT in educational settings, the quality of student questions remains a critical barrier to effective learning. A pilot study involving 385 questions revealed that 72.3% of student questions lacked essential learning context information, 45.8% had unclear question structure, and 45.5% lacked mathematical professionalism. The current FreePass approach—providing immediate answers regardless of question quality—fails to support students in structuring their questions and expanding their thinking, thereby limiting deep learning opportunities.

### Purpose

This study designed and developed MAICE (Mathematical AI Chatbot for Education), a multi-agent system that supports question clarification based on Dewey's reflective thinking theory and Bloom's knowledge taxonomy. The system was specifically applied to the mathematical induction unit for high school grade 2 students, aiming to empirically demonstrate improved learning outcomes through enhanced question quality.

### Methods

This study employed Design-Based Research (DBR) combined with a quasi-experimental design. Fifty-nine high school grade 2 students from Busan Metropolitan City were randomly assigned to either Agent mode (clarification process provided, n=30) or Freepass mode (immediate answers provided, n=29). The study was conducted over approximately two weeks from October 20 to November 1, 2025, utilizing A/B testing methodology.

The QAC Checklist (Question-Answer-Context Checklist, 40 points, 8 sub-items) was developed to evaluate question quality (mathematical professionalism, question structure, learning context), answer quality (learner customization, explanation systematicity, learning expandability), and dialogue context (dialogue consistency, learning support). The QAC Checklist demonstrated excellent internal consistency (Cronbach's α = 0.879), and exploratory factor analysis confirmed a three-factor structure explaining 69.9% of total variance. Additional measures included learning achievement tests (100 points), learning satisfaction surveys (5-point scale, 7 items), and metacognitive ability assessments (5-point scale, 5 items).

Statistical analyses employed independent samples t-tests, paired samples t-tests, Welch's t-tests, and Mann-Whitney U tests. Effect sizes were calculated using Cohen's d, Hedge's g, and Cliff's delta. 95% confidence intervals for mean differences were estimated using Bootstrap methods (1,000 resampling iterations).

### Results

**1. Immediate Effects of Clarification Process**

Single-session analysis revealed that Agent mode was statistically significantly superior in learning support (C2) items (Agent 3.74 vs. Freepass 3.34, one-tailed p=0.034, Cohen's d=0.275). Agent mode also showed clear superiority across the entire dialogue context domain, including dialogue consistency (C1) and learning support (C2) (Agent 10.46 vs. Freepass 9.78, difference +0.68, Cohen's d=0.182).

**2. Empirical Evidence of Cumulative Learning Effects**

Analysis of 40 students who used the system more than twice showed that Agent mode users increased by an average of 0.63 points, while Freepass mode users decreased by 0.36 points (difference +0.99 points, Cohen's d=0.298). Specifically, Agent mode demonstrated advantages in question scores (Agent +2.18 vs. Freepass +0.52, difference +1.65, d=0.307) and answer comprehension (Agent +0.41 vs. Freepass -0.78, difference +1.19, d=0.232).

**3. Statistically Significant Effects for Lower-Achieving Students**

Analysis of session improvement for students in the bottom 33% of multiple-choice scores (~33.6 points) revealed that Agent mode showed statistically significantly greater improvement than Freepass mode (Agent +0.91 vs. Freepass -0.70, difference +1.61, p=0.040, Cohen's d=1.204). Similar patterns were observed for students in the bottom 33% of total midterm scores (Agent +0.52 vs. Freepass -0.58, difference +1.10, d=0.759).

**4. Clarification Performance and Patterns**

Clarification questions were performed in 83.3% of all Agent mode sessions, with 80.0% of these leading to excellent learning support (context_score ≥ 4 points). Clarification question types were classified as choice-based (45%), problem-focused (32%), proof-step specification (15%), and context-seeking (8%).

### Conclusions and Implications

This study empirically demonstrated through A/B testing that question clarification processes enhance learning effectiveness. Specifically, it confirmed that Dewey's reflective thinking theory, when applied to AI educational tools, actually improves learning outcomes, and that these experiences become internalized as students' metacognitive abilities.

The most significant finding was that Agent mode showed statistically significant learning effects for lower-achieving students (p=0.040, d=1.204), presenting a concrete pathway for AI technology to contribute to closing educational gaps. For lower-achieving students lacking procedural knowledge, the clarification process identified comprehension levels and guided step-by-step concept relearning, resulting in substantial score improvements, whereas Freepass mode actually reinforced passive learning patterns.

The theoretical contributions of this study include establishing the pedagogical foundation of clarification processes, presenting a comprehensive evaluation framework that analyzes not only single-session quality but also cumulative learning effects and differential effects by academic level, and establishing causal relationships between clarification processes and learning outcomes through randomized A/B testing.

Practical contributions include demonstrating statistically significant learning effects for lower-achieving students, thereby proving the system's potential as a practical tool for closing educational gaps; providing specific guidelines that AI tutors should prioritize clarification over immediate answer provision; and presenting immediately applicable technical solutions for actual classroom environments through Docker-based deployment and multiprocess agent systems.

This study empirically demonstrated that AI educational tools have genuine educational value not simply by providing correct answers, but by stimulating students' thinking processes and enhancing their questioning abilities. MAICE presents a model for effective AI educational systems that combines modern AI technology with the solid pedagogical foundations of Dewey's reflective thinking and Bloom's knowledge taxonomy, bridging theory and practice.

---

**Keywords**: question clarification, AI agent, reflective thinking, mathematical induction, multi-agent system, Dewey, educational gap reduction, A/B testing

