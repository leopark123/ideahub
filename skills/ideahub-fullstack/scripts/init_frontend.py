#!/usr/bin/env python3
"""
IdeaHub 前端项目初始化脚本
用法: python init_frontend.py [project_path]
"""

import os
import sys
from pathlib import Path

def create_file(path: Path, content: str = ""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"  📄 {path}")

def init_frontend(base_path: Path):
    print(f"\n🚀 初始化 IdeaHub 前端项目: {base_path}\n")
    
    # package.json
    package_json = '''{
  "name": "ideahub-web",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "@tanstack/react-query": "^5.17.0",
    "zustand": "^4.4.0",
    "axios": "^1.6.0",
    "clsx": "^2.1.0",
    "date-fns": "^3.2.0",
    "lucide-react": "^0.303.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "eslint": "^8.56.0",
    "@typescript-eslint/eslint-plugin": "^6.19.0",
    "@typescript-eslint/parser": "^6.19.0",
    "eslint-plugin-react-hooks": "^4.6.0"
  }
}
'''
    create_file(base_path / "package.json", package_json)
    
    # vite.config.ts
    vite_config = '''import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
'''
    create_file(base_path / "vite.config.ts", vite_config)
    
    # tsconfig.json
    tsconfig = '''{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
'''
    create_file(base_path / "tsconfig.json", tsconfig)
    
    # tsconfig.node.json
    tsconfig_node = '''{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
'''
    create_file(base_path / "tsconfig.node.json", tsconfig_node)
    
    # tailwind.config.js
    tailwind_config = '''/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
        },
        secondary: {
          500: '#10b981',
          600: '#059669',
        },
      },
    },
  },
  plugins: [],
}
'''
    create_file(base_path / "tailwind.config.js", tailwind_config)
    
    # postcss.config.js
    postcss_config = '''export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
'''
    create_file(base_path / "postcss.config.js", postcss_config)
    
    # index.html
    index_html = '''<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>IdeaHub - 创意孵化平台</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
'''
    create_file(base_path / "index.html", index_html)
    
    # src/main.tsx
    main_tsx = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './styles/globals.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      retry: 1,
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);
'''
    create_file(base_path / "src/main.tsx", main_tsx)
    
    # src/App.tsx
    app_tsx = '''import { Routes, Route } from 'react-router-dom';
import { Navbar } from '@/components/layout/Navbar';
import Home from '@/pages/Home';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
'''
    create_file(base_path / "src/App.tsx", app_tsx)
    
    # src/styles/globals.css
    globals_css = '''@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
'''
    create_file(base_path / "src/styles/globals.css", globals_css)
    
    # src/api/client.ts
    client_ts = '''import axios from 'axios';
import { useAuthStore } from '@/stores/authStore';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = '/auth/login';
    }
    return Promise.reject(error);
  }
);
'''
    create_file(base_path / "src/api/client.ts", client_ts)
    
    # src/stores/authStore.ts
    auth_store_ts = '''import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  nickname: string;
  avatar?: string;
  role: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      
      login: (token, user) => set({
        token,
        user,
        isAuthenticated: true,
      }),
      
      logout: () => set({
        token: null,
        user: null,
        isAuthenticated: false,
      }),
      
      setUser: (user) => set({ user }),
    }),
    {
      name: 'ideahub-auth',
      partialize: (state) => ({ token: state.token }),
    }
  )
);
'''
    create_file(base_path / "src/stores/authStore.ts", auth_store_ts)
    
    # src/components/layout/Navbar.tsx
    navbar_tsx = '''import { Link } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

export const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuthStore();

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="text-2xl font-bold text-primary-600">
              💡 IdeaHub
            </Link>
            <div className="hidden md:flex ml-10 space-x-8">
              <Link to="/" className="text-gray-600 hover:text-gray-900">
                发现项目
              </Link>
              <Link to="/partners" className="text-gray-600 hover:text-gray-900">
                找合伙人
              </Link>
              <Link to="/crowdfunding" className="text-gray-600 hover:text-gray-900">
                众筹大厅
              </Link>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <span className="text-gray-600">{user?.nickname}</span>
                <button
                  onClick={logout}
                  className="text-gray-600 hover:text-gray-900"
                >
                  退出
                </button>
              </>
            ) : (
              <Link
                to="/auth/login"
                className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
              >
                登录
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};
'''
    create_file(base_path / "src/components/layout/Navbar.tsx", navbar_tsx)
    
    # src/pages/Home.tsx
    home_tsx = '''export default function Home() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="text-center py-16">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          让好想法遇见对的人
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          创意孵化 · 合伙匹配 · 项目众筹
        </p>
        <button className="bg-primary-600 text-white px-8 py-3 rounded-lg text-lg hover:bg-primary-700">
          发布你的想法
        </button>
      </div>
    </div>
  );
}
'''
    create_file(base_path / "src/pages/Home.tsx", home_tsx)
    
    # src/types/index.ts
    types_ts = '''export interface User {
  id: string;
  email: string;
  nickname: string;
  avatar?: string;
  bio?: string;
  role: 'user' | 'creator' | 'investor' | 'admin';
  skills: string[];
  isVerified: boolean;
  createdAt: string;
}

export interface Project {
  id: string;
  title: string;
  slogan?: string;
  coverImage?: string;
  category: string;
  stage: 'idea' | 'building' | 'funding' | 'launched';
  content?: string;
  tags: string[];
  viewCount: number;
  likeCount: number;
  owner: Pick<User, 'id' | 'nickname' | 'avatar'>;
  createdAt: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  pages: number;
}
'''
    create_file(base_path / "src/types/index.ts", types_ts)
    
    # .env.example
    env_example = '''VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
'''
    create_file(base_path / ".env.example", env_example)
    
    # .gitignore
    gitignore = '''node_modules/
dist/
.env
.env.local
*.log
.DS_Store
'''
    create_file(base_path / ".gitignore", gitignore)
    
    print("\n✅ 前端项目初始化完成!")
    print("\n📋 下一步:")
    print("   1. cd", base_path)
    print("   2. npm install")
    print("   3. cp .env.example .env")
    print("   4. npm run dev")

if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ideahub-web")
    init_frontend(path)
