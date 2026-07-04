const modules = [
  // =====================
  // PATHS
  // =====================
  {
    id: 1,
    parent_id: null,
    module_type: "path",
    title: "HTML & CSS",
    description: "Learn the fundamentals of web development with HTML and CSS.",
    estimated_completion_time: "6 weeks",
    created_by: 1,
    order_index: 1,
  },
  {
    id: 2,
    parent_id: null,
    module_type: "path",
    title: "JavaScript: Basic to Advanced",
    description: "Master JavaScript from fundamentals to advanced concepts.",
    estimated_completion_time: "8 weeks",
    created_by: 1,
    order_index: 2,
  },
  {
    id: 3,
    parent_id: null,
    module_type: "path",
    title: "React JS",
    description: "Build modern frontend applications using React.",
    estimated_completion_time: "6 weeks",
    created_by: 1,
    order_index: 3,
  },
  {
    id: 4,
    parent_id: null,
    module_type: "path",
    title: "Git & GitHub",
    description: "Learn version control and collaboration using Git and GitHub.",
    estimated_completion_time: "2 weeks",
    created_by: 1,
    order_index: 4,
  },
  {
    id: 5,
    parent_id: null,
    module_type: "path",
    title: "Communication Skills",
    description: "Improve your communication and interview skills.",
    estimated_completion_time: "4 weeks",
    created_by: 1,
    order_index: 5,
  },

  // =====================
  // HTML & CSS Modules
  // =====================
  {
    id: 11,
    parent_id: 1,
    module_type: "module",
    title: "HTML Basics",
    description: "Learn the fundamentals of HTML.",
    estimated_completion_time: "1 week",
    created_by: 1,
    order_index: 1,
  },
  {
    id: 12,
    parent_id: 1,
    module_type: "module",
    title: "CSS Basics",
    description: "Learn styling with CSS.",
    estimated_completion_time: "2 weeks",
    created_by: 1,
    order_index: 2,
  },
  {
    id: 13,
    parent_id: 1,
    module_type: "module",
    title: "Responsive Design",
    description: "Build responsive websites.",
    estimated_completion_time: "1 week",
    created_by: 1,
    order_index: 3,
  },

  // =====================
  // JavaScript Modules
  // =====================
  {
    id: 21,
    parent_id: 2,
    module_type: "module",
    title: "JavaScript Fundamentals",
    description: "Variables, loops, functions and arrays.",
    estimated_completion_time: "2 weeks",
    created_by: 1,
    order_index: 1,
  },
  {
    id: 22,
    parent_id: 2,
    module_type: "module",
    title: "ES6+ Features",
    description: "Modern JavaScript syntax and features.",
    estimated_completion_time: "2 weeks",
    created_by: 1,
    order_index: 2,
  },
  {
    id: 23,
    parent_id: 2,
    module_type: "module",
    title: "DOM Manipulation",
    description: "Interact with web pages using JavaScript.",
    estimated_completion_time: "2 weeks",
    created_by: 1,
    order_index: 3,
  },
  {
    id: 24,
    parent_id: 2,
    module_type: "module",
    title: "Async JavaScript",
    description: "Promises, async-await and APIs.",
    estimated_completion_time: "2 weeks",
    created_by: 1,
    order_index: 4,
  },

  // =====================
  // React Modules
  // =====================
  {
    id: 31,
    parent_id: 3,
    module_type: "module",
    title: "React Fundamentals",
    description: "Introduction to React.",
    estimated_completion_time: "1 week",
    created_by: 1,
    order_index: 1,
  },
  {
    id: 32,
    parent_id: 3,
    module_type: "module",
    title: "Components & Props",
    description: "Reusable UI with components.",
    estimated_completion_time: "1 week",
    created_by: 1,
    order_index: 2,
  },
  {
    id: 33,
    parent_id: 3,
    module_type: "module",
    title: "Hooks",
    description: "Learn React hooks.",
    estimated_completion_time: "2 weeks",
    created_by: 1,
    order_index: 3,
  },
  {
    id: 34,
    parent_id: 3,
    module_type: "module",
    title: "Routing & State Management",
    description: "React Router and state management.",
    estimated_completion_time: "2 weeks",
    created_by: 1,
    order_index: 4,
  },

  // =====================
  // Git & GitHub Modules
  // =====================
  {
    id: 41,
    parent_id: 4,
    module_type: "module",
    title: "Git Basics",
    description: "Learn Git fundamentals.",
    estimated_completion_time: "1 week",
    created_by: 1,
    order_index: 1,
  },
  {
    id: 42,
    parent_id: 4,
    module_type: "module",
    title: "Branching & Merging",
    description: "Work with branches and merges.",
    estimated_completion_time: "1 week",
    created_by: 1,
    order_index: 2,
  },
  {
    id: 43,
    parent_id: 4,
    module_type: "module",
    title: "GitHub Collaboration",
    description: "Collaborate using GitHub.",
    estimated_completion_time: "1 week",
    created_by: 1,
    order_index: 3,
  },

  // =====================
  // Communication Modules
  // =====================
  {
    id: 51,
    parent_id: 5,
    module_type: "module",
    title: "Verbal Communication",
    description: "Develop speaking confidence.",
    estimated_completion_time: "1 week",
    created_by: 1,
    order_index: 1,
  },
  {
    id: 52,
    parent_id: 5,
    module_type: "module",
    title: "Presentation Skills",
    description: "Learn to present effectively.",
    estimated_completion_time: "1 week",
    created_by: 1,
    order_index: 2,
  },
  {
    id: 53,
    parent_id: 5,
    module_type: "module",
    title: "Interview Skills",
    description: "Ace interviews with confidence.",
    estimated_completion_time: "2 weeks",
    created_by: 1,
    order_index: 3,
  },
];

export default modules;