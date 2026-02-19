export interface WeekPlan {
  week: number;
  title: string;
  topics: string[];
  assignment: string;
}

export interface Curriculum {
  title: string;
  level: string;
  duration: string;
  learningOutcomes: string[];
  weeks: WeekPlan[];
}

export function generateMockCurriculum(subject: string, level: string, duration: string, goals: string): Curriculum {
  // Parse duration to determine number of weeks
  const durationLower = duration.toLowerCase();
  let numWeeks = 6;
  const weekMatch = durationLower.match(/(\d+)\s*week/);
  const monthMatch = durationLower.match(/(\d+)\s*month/);
  if (weekMatch) numWeeks = parseInt(weekMatch[1]);
  else if (monthMatch) numWeeks = parseInt(monthMatch[1]) * 4;
  numWeeks = Math.max(2, Math.min(numWeeks, 16));

  const weekTemplates: Record<string, string[][]> = {
    Beginner: [
      ["Introduction & Fundamentals", "Core Concepts Overview", "Setting Up Your Environment"],
      ["Basic Terminology", "Key Principles", "Foundational Frameworks"],
      ["Hands-On Basics", "Guided Practice", "Simple Exercises"],
      ["Building Blocks", "Step-by-Step Walkthroughs", "Practical Examples"],
      ["Intermediate Concepts", "Connecting Ideas", "Pattern Recognition"],
      ["Applied Learning", "Mini Projects", "Peer Discussion"],
      ["Review & Consolidation", "Practice Assessment", "Knowledge Check"],
      ["Capstone Project", "Final Presentation", "Course Wrap-up"],
    ],
    Intermediate: [
      ["Advanced Fundamentals Review", "Gap Analysis", "Goal Setting"],
      ["Deep Dive into Core Theory", "Case Studies", "Analytical Frameworks"],
      ["Advanced Techniques", "Best Practices", "Industry Standards"],
      ["Complex Problem Solving", "Real-World Scenarios", "Critical Thinking"],
      ["Integration & Systems Thinking", "Cross-Domain Applications", "Synthesis"],
      ["Project Planning", "Design Methodology", "Implementation Strategy"],
      ["Advanced Project Work", "Iteration & Feedback", "Quality Assurance"],
      ["Portfolio Development", "Professional Presentation", "Peer Review"],
    ],
    Advanced: [
      ["State of the Art Review", "Research Methodology", "Advanced Theory"],
      ["Cutting-Edge Techniques", "Innovation Frameworks", "Experimental Design"],
      ["Expert-Level Analysis", "Complex Systems", "Advanced Modeling"],
      ["Research & Development", "Original Contributions", "Peer Review"],
      ["Leadership in Practice", "Mentoring Others", "Knowledge Transfer"],
      ["Industry Applications", "Consulting Scenarios", "Strategic Planning"],
      ["Advanced Capstone Project", "Publication-Ready Work", "Presentation"],
      ["Professional Development", "Career Strategy", "Continuing Education"],
    ],
  };

  const templates = weekTemplates[level] || weekTemplates.Beginner;

  const weeks: WeekPlan[] = Array.from({ length: numWeeks }, (_, i) => {
    const template = templates[i % templates.length];
    return {
      week: i + 1,
      title: `${template[0]} in ${subject}`,
      topics: [
        `${template[0]} — understanding the key aspects of ${subject}`,
        `${template[1]} — applying concepts to ${subject.toLowerCase()}`,
        `${template[2]} — practical exploration of ${subject.toLowerCase()} techniques`,
      ],
      assignment: i === numWeeks - 1
        ? `Complete a comprehensive final project demonstrating mastery of ${subject}`
        : `${template[1]} exercise: Apply this week's ${subject.toLowerCase()} concepts in a hands-on activity`,
    };
  });

  const learningOutcomes = [
    `Demonstrate a strong ${level.toLowerCase()}-level understanding of ${subject}`,
    `Apply core ${subject.toLowerCase()} concepts to solve real-world problems`,
    `Analyze and evaluate ${subject.toLowerCase()} scenarios using established frameworks`,
    `Create original work that showcases proficiency in ${subject.toLowerCase()}`,
    ...goals.split(/[.,;]/).filter(g => g.trim().length > 5).slice(0, 2).map(g => g.trim()),
  ];

  return {
    title: `${subject} — ${level} Curriculum`,
    level,
    duration,
    learningOutcomes,
    weeks,
  };
}
