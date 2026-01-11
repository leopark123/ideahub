import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { projectsApi, type Project } from '@/api/projects';
import { crowdfundingApi } from '@/api/crowdfunding';

export default function CreateCrowdfunding() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    target_amount: '',
    min_investment: '100',
    max_investment: '',
    start_time: '',
    end_time: '',
  });

  useEffect(() => {
    if (id) {
      loadProject();
    }
  }, [id]);

  const loadProject = async () => {
    try {
      const data = await projectsApi.get(id!);
      setProject(data);
      // Set default dates
      const now = new Date();
      const start = new Date(now.getTime() + 24 * 60 * 60 * 1000); // tomorrow
      const end = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000); // 30 days later
      setFormData((prev) => ({
        ...prev,
        start_time: start.toISOString().slice(0, 16),
        end_time: end.toISOString().slice(0, 16),
      }));
    } catch {
      setError('项目不存在');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!formData.target_amount || parseFloat(formData.target_amount) <= 0) {
      setError('请输入有效的目标金额');
      return;
    }

    if (!formData.start_time || !formData.end_time) {
      setError('请设置开始和结束时间');
      return;
    }

    if (new Date(formData.end_time) <= new Date(formData.start_time)) {
      setError('结束时间必须晚于开始时间');
      return;
    }

    setSubmitting(true);
    try {
      const cf = await crowdfundingApi.create({
        project_id: id!,
        target_amount: parseFloat(formData.target_amount),
        min_investment: parseFloat(formData.min_investment) || 100,
        max_investment: formData.max_investment ? parseFloat(formData.max_investment) : undefined,
        start_time: new Date(formData.start_time).toISOString(),
        end_time: new Date(formData.end_time).toISOString(),
      });

      // 自动启动众筹
      await crowdfundingApi.start(cf.id);

      alert('众筹创建成功！');
      navigate(`/projects/${id}`);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || '创建众筹失败，请稍后再试');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-2xl mx-auto px-4">
          <div className="bg-white rounded-xl shadow-sm p-8 animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
            <div className="space-y-4">
              <div className="h-10 bg-gray-200 rounded"></div>
              <div className="h-10 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-2xl mx-auto px-4 text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">项目不存在</h1>
          <button
            onClick={() => navigate(-1)}
            className="text-primary-600 hover:text-primary-700"
          >
            返回
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-2xl mx-auto px-4">
        <div className="bg-white rounded-xl shadow-sm p-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">创建众筹</h1>
          <p className="text-gray-600 mb-6">为项目「{project.title}」发起众筹</p>

          {error && (
            <div className="mb-6 bg-red-50 text-red-600 p-4 rounded-lg">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                目标金额（元）<span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                required
                min="1"
                value={formData.target_amount}
                onChange={(e) => setFormData({ ...formData, target_amount: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                placeholder="10000"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  最低投资金额（元）
                </label>
                <input
                  type="number"
                  min="1"
                  value={formData.min_investment}
                  onChange={(e) => setFormData({ ...formData, min_investment: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                  placeholder="100"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  最高投资金额（元）
                </label>
                <input
                  type="number"
                  min="1"
                  value={formData.max_investment}
                  onChange={(e) => setFormData({ ...formData, max_investment: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                  placeholder="不限制"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  开始时间 <span className="text-red-500">*</span>
                </label>
                <input
                  type="datetime-local"
                  required
                  value={formData.start_time}
                  onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  结束时间 <span className="text-red-500">*</span>
                </label>
                <input
                  type="datetime-local"
                  required
                  value={formData.end_time}
                  onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>

            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-blue-800 mb-2">众筹说明</h3>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>众筹创建后会立即开始</li>
                <li>众筹期间用户可以投资支持您的项目</li>
                <li>众筹结束后，如果达到目标金额则众筹成功</li>
                <li>未达到目标金额将自动退款给投资者</li>
              </ul>
            </div>

            <div className="flex justify-end gap-4 pt-4 border-t">
              <button
                type="button"
                onClick={() => navigate(-1)}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                取消
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
              >
                {submitting ? '创建中...' : '创建众筹'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
