import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { crowdfundingApi, type Crowdfunding } from '@/api/crowdfunding';
import { projectsApi, type Project } from '@/api/projects';

interface CrowdfundingWithProject extends Crowdfunding {
  project?: Project;
}

export default function CrowdfundingPage() {
  const [crowdfundings, setCrowdfundings] = useState<CrowdfundingWithProject[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCrowdfundings();
  }, []);

  const loadCrowdfundings = async () => {
    setLoading(true);
    try {
      const data = await crowdfundingApi.listActive();
      const withProjects = await Promise.all(
        data.map(async (cf) => {
          try {
            const project = await projectsApi.getById(cf.project_id);
            return { ...cf, project };
          } catch {
            return cf;
          }
        })
      );
      setCrowdfundings(withProjects);
    } catch (error) {
      console.error('Failed to load crowdfundings:', error);
    } finally {
      setLoading(false);
    }
  };

  const getProgressPercentage = (current: number, target: number) => {
    return Math.min((current / target) * 100, 100);
  };

  const getDaysRemaining = (endTime: string) => {
    const end = new Date(endTime);
    const now = new Date();
    const diff = end.getTime() - now.getTime();
    return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
  };

  const formatAmount = (amount: number) => {
    if (amount >= 10000) {
      return `${(amount / 10000).toFixed(1)}万`;
    }
    return amount.toLocaleString();
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">众筹大厅</h1>
          <p className="text-gray-600">支持优质项目，参与创业投资</p>
        </div>

        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500">
              共 {crowdfundings.length} 个进行中的众筹
            </span>
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-white rounded-xl shadow-sm overflow-hidden animate-pulse">
                <div className="h-40 bg-gray-200"></div>
                <div className="p-4 space-y-3">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-full"></div>
                  <div className="h-8 bg-gray-200 rounded"></div>
                </div>
              </div>
            ))}
          </div>
        ) : crowdfundings.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {crowdfundings.map((cf) => {
              const progress = getProgressPercentage(cf.current_amount, cf.target_amount);
              const daysRemaining = getDaysRemaining(cf.end_time);

              return (
                <div
                  key={cf.id}
                  className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow overflow-hidden"
                >
                  <div className="relative">
                    <img
                      src={cf.project?.cover_url || 'https://via.placeholder.com/400x200?text=Project'}
                      alt={cf.project?.title || '众筹项目'}
                      className="w-full h-40 object-cover"
                    />
                    <div className="absolute top-3 right-3">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        daysRemaining > 7
                          ? 'bg-green-500 text-white'
                          : daysRemaining > 0
                          ? 'bg-yellow-500 text-white'
                          : 'bg-gray-500 text-white'
                      }`}>
                        {daysRemaining > 0 ? `剩余 ${daysRemaining} 天` : '已结束'}
                      </span>
                    </div>
                  </div>

                  <div className="p-4">
                    <h3 className="font-semibold text-gray-900 mb-2 line-clamp-1">
                      {cf.project?.title || '众筹项目'}
                    </h3>
                    <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                      {cf.project?.description || '暂无描述'}
                    </p>

                    <div className="mb-4">
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-500">已筹</span>
                        <span className="font-semibold text-primary-600">
                          {progress.toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-primary-600 h-2 rounded-full transition-all"
                          style={{ width: `${progress}%` }}
                        ></div>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-2 text-center mb-4">
                      <div>
                        <div className="text-lg font-bold text-gray-900">
                          ¥{formatAmount(cf.current_amount)}
                        </div>
                        <div className="text-xs text-gray-500">已筹金额</div>
                      </div>
                      <div>
                        <div className="text-lg font-bold text-gray-900">
                          {cf.investor_count}
                        </div>
                        <div className="text-xs text-gray-500">支持人数</div>
                      </div>
                      <div>
                        <div className="text-lg font-bold text-gray-900">
                          ¥{formatAmount(cf.target_amount)}
                        </div>
                        <div className="text-xs text-gray-500">目标金额</div>
                      </div>
                    </div>

                    <Link
                      to={`/projects/${cf.project_id}`}
                      className="block w-full py-2 text-center bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                    >
                      查看详情
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="mt-4 text-lg font-medium text-gray-900">暂无众筹活动</h3>
            <p className="mt-2 text-gray-500">目前没有进行中的众筹项目</p>
          </div>
        )}
      </div>
    </div>
  );
}
