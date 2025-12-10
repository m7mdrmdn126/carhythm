# CaRhythm Story Mode Frontend

An engaging, mobile-first React frontend for the CaRhythm Career Assessment platform, featuring Instagram Stories-style narrative assessments.

## 🎯 Features

- **Story Mode Experience**: Narrative-driven assessments with scene settings and character scenarios
- **5 Question Types**: Slider, MCQ Single/Multiple, Ordering (drag-drop), Essay
- **Mobile-First Design**: Optimized for Gen Z/Alpha mobile users
- **Responsive**: Works beautifully on mobile, tablet, and desktop
- **Progress Tracking**: Visual progress bar with gamification
- **Smooth Animations**: Framer Motion for page transitions
- **Theme Support**: Dynamic scene themes (workshop, mindpalace, flow, cosmic)

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## 📦 Tech Stack

- React 18.2+ with Vite 7.2+
- React Router 6 for routing
- Axios for API calls
- Framer Motion for animations
- CSS Variables design system

## 🏗️ Project Structure

```
src/
├── components/     # Reusable UI components
├── pages/          # Route pages (Welcome, Question, Complete)
├── services/       # API integration
├── hooks/          # Custom React hooks
└── styles/         # Global styles & design tokens
```

## 🔌 API Integration

Backend API: `http://localhost:8000/api/v2/`

Key endpoints:
- GET `/modules` - Assessment modules
- GET `/questions` - Questions for page
- POST `/session/start` - Start session
- POST `/answers/submit` - Submit answer
- POST `/student/info` - Submit student info

## 📱 Responsive Breakpoints

- Mobile: default (320px+)
- Tablet: 768px+
- Desktop: 1024px+

## 🎨 Customization

Edit `.env` for API configuration:
```env
VITE_API_BASE_URL=http://localhost:8000
```

Edit `src/styles/variables.css` for design tokens.

## 📄 License

Copyright © 2025 CaRhythm. All rights reserved.


The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
