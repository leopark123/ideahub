import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { projectsApi, type Project } from '@/api/projects';
import { crowdfundingApi, type Crowdfunding } from '@/api/crowdfunding';
import { ProjectCard } from '@/components/ProjectCard';
import { useAuthStore } from '@/stores/authStore';

const categories = [
  { key: '', label: '全部' },
  { key: 'tech', label: '科技' },
  { key: 'art', label: '艺术' },
  { key: 'education', label: '教育' },
  { key: 'health', label: '健康' },
  { key: 'social', label: '社会公益' },
  { key: 'entertainment', label: '娱乐' },
  { key: 'finance', label: '金融' },
];

export default function Home() {
  const { isAuthenticated } = useAuthStore();
  const [projects, setProjects] = useState<Project[]>([]);
  const [crowdfundings, setCrowdfundings] = useState<Crowdfunding[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [keyword, setKeyword] = useState('');

  useEffect(() => {
    loadProjects();
    loadCrowdfundings();
  }, [selectedCategory]);

  const loadProjects = async () => {
    setLoading(true);
    try {
      const response = await projectsApi.list({
        page: 1,
        page_size: 12,
        category: selectedCategory || undefined,
        status: 'active',
        keyword: keyword || undefined,
      });
      setProjects(response.items);
    } catch (error) {
      console.error('Failed to load projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCrowdfundings = async () => {
    try {
      const response = await crowdfundingApi.list({ page_size: 3, status: 'active' });
      setCrowdfundings(response.items);
    } catch (error) {
      console.error('Failed to load crowdfundings:', error);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadProjects();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-800 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            让好想法遇见对的人
          </h1>
          <p className="text-xl text-primary-100 mb-8">
            创意孵化 · 合伙匹配 · 项目众筹
          </p>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="max-w-2xl mx-auto">
            <div className="flex bg-white rounded-lg shadow-lg overflow-hidden">
              <input
                type="text"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                placeholder="搜索你感兴趣的项目..."
                className="flex-1 px-6 py-4 text-gray-900 focus:outline-none"
              />
              <button
                type="submit"
                className="px-8 bg-primary-600 hover:bg-primary-700 text-white font-medium"
              >
                搜索
              </button>
            </div>
          </form>

          <div className="mt-8 flex justify-center space-x-4">
            {isAuthenticated ? (
              <Link
                to="/projects/new"
                className="inline-flex items-center px-8 py-3 bg-white text-primary-600 rounded-lg font-medium hover:bg-gray-100 transition-colors"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                发布你的想法
              </Link>
            ) : (
              <Link
                to="/auth/register"
                className="inline-flex items-center px-8 py-3 bg-white text-primary-600 rounded-lg font-medium hover:bg-gray-100 transition-colors"
              >
                开始你的创业之旅
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* Category Filter */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex flex-wrap gap-2">
          {categories.map((cat) => (
            <button
              key={cat.key}
              onClick={() => setSelectedCategory(cat.key)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                selectedCategory === cat.key
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-100'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Projects Grid */}
      <div className="max-w-7xl mx-auto px-4 pb-12">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">热门项目</h2>
          <Link to="/projects" className="text-primary-600 hover:text-primary-700 font-medium">
            查看全部 &rarr;
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="bg-white rounded-xl shadow-sm overflow-hidden animate-pulse">
                <div className="h-48 bg-gray-200"></div>
                <div className="p-4 space-y-3">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-full"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        ) : projects.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {projects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <h3 className="mt-4 text-lg font-medium text-gray-900">暂无项目</h3>
            <p className="mt-2 text-gray-500">还没有发布的项目，来发布第一个吧！</p>
            <Link
              to={isAuthenticated ? '/projects/new' : '/auth/register'}
              className="mt-4 inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              {isAuthenticated ? '发布项目' : '注册账号'}
            </Link>
          </div>
        )}
      </div>

      {/* Featured Crowdfundings */}
      {crowdfundings.length > 0 && (
        <div className="max-w-7xl mx-auto px-4 pb-12">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">热门众筹</h2>
            <Link to="/crowdfunding" className="text-primary-600 hover:text-primary-700 font-medium">
              查看全部 &rarr;
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {crowdfundings.map((cf) => (
              <Link
                key={cf.id}
                to={`/projects/${cf.project_id}`}
                className="block bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow overflow-hidden"
              >
                <div className="p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-1">{cf.title}</h3>
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">{cf.description}</p>
                  <div className="mb-4">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">已筹集</span>
                      <span className="font-semibold text-primary-600">
                        {((cf.current_amount / cf.target_amount) * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full"
                        style={{ width: `${Math.min((cf.current_amount / cf.target_amount) * 100, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">
                      ¥{cf.current_amount.toLocaleString()} / ¥{cf.target_amount.toLocaleString()}
                    </span>
                    <span className="text-gray-500">{cf.investor_count} 人支持</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-gray-100 py-12">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">开始你的创业之旅</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Link
              to={isAuthenticated ? '/projects/new' : '/auth/register'}
              className="flex flex-col items-center p-8 bg-white rounded-xl shadow-sm hover:shadow-md transition-all"
            >
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">发布创意</h3>
              <p className="text-sm text-gray-600 text-center">把你的好想法分享出来，吸引志同道合的伙伴</p>
            </Link>
            <Link
              to="/partners"
              className="flex flex-col items-center p-8 bg-white rounded-xl shadow-sm hover:shadow-md transition-all"
            >
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">寻找合伙人</h3>
              <p className="text-sm text-gray-600 text-center">浏览正在招募的项目，找到适合你的团队</p>
            </Link>
            <Link
              to="/crowdfunding"
              className="flex flex-col items-center p-8 bg-white rounded-xl shadow-sm hover:shadow-md transition-all"
            >
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">参与众筹</h3>
              <p className="text-sm text-gray-600 text-center">支持你看好的项目，共享成功的喜悦</p>
            </Link>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-white py-12">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold text-primary-600">1,000+</div>
              <div className="text-gray-600 mt-1">创意项目</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary-600">5,000+</div>
              <div className="text-gray-600 mt-1">注册用户</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary-600">¥500万+</div>
              <div className="text-gray-600 mt-1">众筹金额</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary-600">200+</div>
              <div className="text-gray-600 mt-1">成功项目</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
