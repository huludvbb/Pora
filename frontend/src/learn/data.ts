// Static seed content for the Learn mini-app. Kept in a single module so
// screens can share the same source of truth and stay in sync. Real data
// can later swap in via backend endpoints without changing screen code.

import { learnColors } from "./theme";

// ---- Grammar Guide ---------------------------------------------------------
export interface GrammarLesson {
  id: string;
  level: string;
  title: string;
  summary: string;
  body: string;
  examples: string[];
  color: string;
  emoji: string;
  minutes: number;
}

export const GRAMMAR_LESSONS: GrammarLesson[] = [
  {
    id: "articles",
    level: "A1",
    title: "Articles: el, la, los, las",
    summary: "Match articles with the gender and number of the noun.",
    body:
      "Spanish nouns come with a grammatical gender. Definite articles ('the') change with gender and number: el (masc. sg.), la (fem. sg.), los (masc. pl.), las (fem. pl.). Indefinite articles work the same: un, una, unos, unas.",
    examples: [
      "el libro — the book",
      "la mesa — the table",
      "los amigos — the friends",
      "unas ideas — some ideas",
    ],
    color: learnColors.yellow,
    emoji: "📘",
    minutes: 4,
  },
  {
    id: "ser-estar",
    level: "A2",
    title: "Ser vs. Estar",
    summary: "Both mean 'to be' — but pick the one that matches your intent.",
    body:
      "Use SER for permanent identity: profession, nationality, character, time, origin. Use ESTAR for temporary state, location, emotion, or ongoing action.",
    examples: [
      "Soy estudiante. — I'm a student. (identity)",
      "Estoy cansado. — I'm tired. (temporary)",
      "El café está en la mesa. — The coffee is on the table. (location)",
      "Es lunes. — It's Monday. (time)",
    ],
    color: "#DABFFF",
    emoji: "🔀",
    minutes: 6,
  },
  {
    id: "past-preterite",
    level: "B1",
    title: "The Preterite Past",
    summary: "Talk about finished actions with a clear beginning and end.",
    body:
      "The preterite is used for completed past actions. Regular endings for -ar verbs are -é, -aste, -ó, -amos, -asteis, -aron. For -er/-ir verbs: -í, -iste, -ió, -imos, -isteis, -ieron.",
    examples: [
      "Ayer comí paella. — Yesterday I ate paella.",
      "Ella habló con el profesor. — She spoke with the teacher.",
      "Fuimos al cine el viernes. — We went to the movies on Friday.",
    ],
    color: learnColors.green,
    emoji: "⏪",
    minutes: 8,
  },
  {
    id: "subjunctive",
    level: "B2",
    title: "The Subjunctive Mood",
    summary: "Doubt, desire, emotion — the subjunctive lives here.",
    body:
      "Use the subjunctive after triggers of doubt, desire, emotion, and impersonal expressions. Present subjunctive endings for -ar verbs: -e, -es, -e, -emos, -éis, -en; for -er/-ir: -a, -as, -a, -amos, -áis, -an.",
    examples: [
      "Espero que estés bien. — I hope you are well.",
      "Es posible que llueva. — It's possible that it will rain.",
      "Quiero que vengas. — I want you to come.",
    ],
    color: learnColors.orange,
    emoji: "🎭",
    minutes: 10,
  },
  {
    id: "por-para",
    level: "B1",
    title: "Por vs. Para",
    summary: "Two little words, huge difference.",
    body:
      "POR = cause / reason / duration / exchange / means. PARA = purpose / destination / deadline / recipient. Tip: if you can say 'because of' or 'through', use POR. If 'in order to' or 'for the sake of', use PARA.",
    examples: [
      "Gracias por venir. — Thanks for coming.",
      "Este regalo es para ti. — This gift is for you.",
      "Salgo para Madrid mañana. — I leave for Madrid tomorrow.",
    ],
    color: "#7DD3FC",
    emoji: "🔁",
    minutes: 5,
  },
];

// ---- Courses ---------------------------------------------------------------
export interface Course {
  id: string;
  title: string;
  category: string;
  level: string;
  lessons: number;
  minutes: number;
  color: string;
  emoji: string;
  description: string;
  outline: { title: string; body: string }[];
}

export const COURSES: Course[] = [
  {
    id: "everyday-travel",
    title: "Everyday Travel Spanish",
    category: "Travel",
    level: "A2",
    lessons: 12,
    minutes: 90,
    color: learnColors.yellow,
    emoji: "✈️",
    description:
      "Airports, hotels, restaurants, taxis — the survival phrases you actually need on your next trip.",
    outline: [
      { title: "At the airport", body: "Boarding, baggage, immigration." },
      { title: "Checking in", body: "Hotel reservations, requests, complaints." },
      { title: "Restaurants", body: "Ordering, allergies, splitting the bill." },
      { title: "Getting around", body: "Taxi, metro, asking for directions." },
    ],
  },
  {
    id: "business-basics",
    title: "Business Communication",
    category: "Career",
    level: "B1",
    lessons: 18,
    minutes: 140,
    color: "#DABFFF",
    emoji: "💼",
    description:
      "Emails, calls, meetings — polished professional Spanish for the workplace.",
    outline: [
      { title: "Formal emails", body: "Greetings, requests, closings." },
      { title: "Presentations", body: "Structure, transitions, Q&A." },
      { title: "Negotiations", body: "Making offers and counter-offers." },
      { title: "Small talk", body: "Networking without the awkwardness." },
    ],
  },
  {
    id: "cafe-conversations",
    title: "Café Conversations",
    category: "Everyday",
    level: "A1",
    lessons: 8,
    minutes: 60,
    color: learnColors.green,
    emoji: "☕",
    description:
      "Warm, friendly chats over coffee: ordering, weather, weekend plans, and casual questions.",
    outline: [
      { title: "Ordering coffee", body: "Custom orders and polite requests." },
      { title: "Weather talk", body: "Descriptions and reactions." },
      { title: "Weekend plans", body: "Suggestions and invites." },
    ],
  },
  {
    id: "grammar-refresh",
    title: "Grammar Refresh",
    category: "Grammar",
    level: "B1",
    lessons: 22,
    minutes: 180,
    color: learnColors.orange,
    emoji: "📐",
    description:
      "A focused sweep through the essentials: tenses, moods, prepositions, and tricky pairs.",
    outline: [
      { title: "Present tense", body: "Regular + high-frequency irregulars." },
      { title: "Past tenses", body: "Preterite vs. imperfect." },
      { title: "Subjunctive intro", body: "Triggers and common phrases." },
    ],
  },
];

// ---- Teachers --------------------------------------------------------------
export interface Teacher {
  id: string;
  name: string;
  emoji: string;
  bg: string;
  country: string;
  languages: string[];
  rating: number;
  reviews: number;
  price: string;
  bio: string;
  specialties: string[];
}

export const TEACHERS: Teacher[] = [
  {
    id: "maria-luisa",
    name: "María Luisa",
    emoji: "👩🏻‍🏫",
    bg: learnColors.yellow,
    country: "Spain",
    languages: ["Spanish", "English"],
    rating: 4.9,
    reviews: 213,
    price: "$18/hr",
    bio: "Certified DELE examiner with 8 years teaching adult learners. Loves grammar puzzles and coffee.",
    specialties: ["Grammar", "DELE prep", "Business Spanish"],
  },
  {
    id: "diego-ramos",
    name: "Diego Ramos",
    emoji: "🧑🏽‍🏫",
    bg: "#DABFFF",
    country: "Mexico",
    languages: ["Spanish", "English"],
    rating: 4.8,
    reviews: 156,
    price: "$14/hr",
    bio: "From Guadalajara — patient, playful, obsessed with pronunciation and idioms.",
    specialties: ["Conversation", "Pronunciation", "Travel Spanish"],
  },
  {
    id: "emily-carter",
    name: "Emily Carter",
    emoji: "👩🏼‍🏫",
    bg: learnColors.green,
    country: "USA",
    languages: ["Spanish", "English", "Portuguese"],
    rating: 4.9,
    reviews: 189,
    price: "$22/hr",
    bio: "Language coach specialising in fluency for busy professionals.",
    specialties: ["Fluency", "Interview prep", "Business"],
  },
];

// ---- Reading Library -------------------------------------------------------
export interface Story {
  id: string;
  title: string;
  level: string;
  minutes: number;
  color: string;
  emoji: string;
  summary: string;
  body: string;
  glossary: { word: string; meaning: string }[];
}

export const STORIES: Story[] = [
  {
    id: "la-cafeteria",
    title: "La cafetería del barrio",
    level: "A1",
    minutes: 3,
    color: learnColors.yellow,
    emoji: "☕",
    summary: "A quiet morning coffee turns into an unexpected chat.",
    body:
      "Marta entra en la cafetería. El aroma del café recién hecho llena el aire. Pide un café con leche y un croissant. La camarera sonríe: '¿Con azúcar?' Marta responde: 'No, gracias.' Al lado, un chico lee un libro. Marta se sienta cerca de la ventana. El día empieza con calma.",
    glossary: [
      { word: "recién hecho", meaning: "freshly made" },
      { word: "camarera", meaning: "waitress" },
      { word: "cerca de", meaning: "near / close to" },
    ],
  },
  {
    id: "el-mercado",
    title: "El mercado los sábados",
    level: "A2",
    minutes: 5,
    color: "#DABFFF",
    emoji: "🛒",
    summary: "Saturday market: fruit, laughter, and a lost list.",
    body:
      "Cada sábado, Luis va al mercado con su lista de compras. Compra tomates, pan y queso. Hoy, olvidó la lista en casa. 'No importa,' piensa. Habla con la vendedora, prueba una manzana y compra flores para su madre. A veces, olvidar la lista trae sorpresas.",
    glossary: [
      { word: "olvidó", meaning: "forgot" },
      { word: "vendedora", meaning: "seller (female)" },
      { word: "sorpresas", meaning: "surprises" },
    ],
  },
  {
    id: "la-carta",
    title: "La carta del abuelo",
    level: "B1",
    minutes: 6,
    color: learnColors.green,
    emoji: "✉️",
    summary: "A yellowed letter, a family secret quietly revealed.",
    body:
      "En un cajón antiguo, Ana encontró una carta amarilla. Era de su abuelo, escrita hace treinta años. Hablaba de un viaje a Argentina, de un amigo lejano y de un sueño que nunca cumplió. Ana leyó la carta con lágrimas en los ojos. Decidió que ella terminaría el viaje por él.",
    glossary: [
      { word: "cajón", meaning: "drawer" },
      { word: "amigo lejano", meaning: "faraway friend" },
      { word: "cumplió", meaning: "fulfilled / achieved" },
    ],
  },
];

// ---- Achievements ----------------------------------------------------------
export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string; // emoji
  color: string;
  earned: boolean;
  progress?: { current: number; total: number };
}

export const ACHIEVEMENTS: Achievement[] = [
  {
    id: "first-steps",
    title: "First Steps",
    description: "Complete your first workout",
    icon: "🌱",
    color: learnColors.green,
    earned: true,
  },
  {
    id: "seven-streak",
    title: "Seven Wonders",
    description: "Reach a 7-day streak",
    icon: "🔥",
    color: learnColors.orange,
    earned: true,
  },
  {
    id: "hundred-words",
    title: "Word Collector",
    description: "Master 100 vocabulary words",
    icon: "📚",
    color: learnColors.yellow,
    earned: false,
    progress: { current: 42, total: 100 },
  },
  {
    id: "grammar-guru",
    title: "Grammar Guru",
    description: "Finish 5 grammar lessons",
    icon: "🧠",
    color: "#DABFFF",
    earned: false,
    progress: { current: 2, total: 5 },
  },
  {
    id: "chatterbox",
    title: "Chatterbox",
    description: "Chat with the AI tutor 10 times",
    icon: "💬",
    color: "#7DD3FC",
    earned: false,
    progress: { current: 3, total: 10 },
  },
  {
    id: "librarian",
    title: "Little Librarian",
    description: "Read 3 short stories",
    icon: "📖",
    color: learnColors.green,
    earned: false,
    progress: { current: 1, total: 3 },
  },
  {
    id: "night-owl",
    title: "Night Owl",
    description: "Practise after 10 PM",
    icon: "🌙",
    color: "#2E2E38",
    earned: true,
  },
  {
    id: "polyglot",
    title: "Polyglot",
    description: "Start a second language",
    icon: "🌍",
    color: learnColors.orange,
    earned: false,
  },
];

// ---- Leaderboard -----------------------------------------------------------
export interface LeaderboardEntry {
  id: string;
  name: string;
  emoji: string;
  xp: number;
  isYou?: boolean;
  country: string;
}

export const LEADERBOARD: LeaderboardEntry[] = [
  { id: "u1", name: "Sofia", emoji: "🦊", xp: 2450, country: "🇪🇸" },
  { id: "u2", name: "Kenji", emoji: "🐼", xp: 2210, country: "🇯🇵" },
  { id: "u3", name: "Aisha", emoji: "🦋", xp: 1980, country: "🇨🇦" },
  { id: "u4", name: "You", emoji: "🙂", xp: 1745, country: "🇧🇩", isYou: true },
  { id: "u5", name: "Marco", emoji: "🐻", xp: 1520, country: "🇮🇹" },
  { id: "u6", name: "Lin", emoji: "🐧", xp: 1380, country: "🇨🇳" },
  { id: "u7", name: "Ava", emoji: "🦁", xp: 1260, country: "🇦🇺" },
  { id: "u8", name: "Priya", emoji: "🐝", xp: 1140, country: "🇮🇳" },
];

// ---- Word of the Day -------------------------------------------------------
export const WORD_OF_DAY = {
  word: "sobremesa",
  language: "Spanish",
  ipa: "/so.βɾeˈme.sa/",
  meaning: "The relaxed conversation lingering at the table after a meal.",
  example: "La sobremesa duró más que la cena.",
  exampleTranslation: "The chat after the meal lasted longer than dinner itself.",
  color: learnColors.yellow,
  emoji: "🍷",
};
