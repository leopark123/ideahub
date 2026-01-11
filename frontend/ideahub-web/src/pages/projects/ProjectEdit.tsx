import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { projectsApi, type CreateProjectData } from '@/api/projects';

const categories = [
  { value: 'tech', label: '科技' },
  { value: 'art', label: '艺术' },
  { value: 'education', label: '教育' },
  { value: 'health', label: '健康' },
  { value: 'social', label: '社会公益' },
  { value: 'entertainment', label: '娱乐' },
  { value: 'finance', label: '金融' },
  { value: 'other', label: '其他' },
];

export default function ProjectEdit() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [loadingProject, setLoadingProject] = useState(true);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState<CreateProjectData>({
    title: '',
    subtitle: '',
    description: '',
    category: 'tech',
    cover_image: '',
    team_size: 1,
    required_skills: [],
  });
  const [skillInput, setSkillInput] = useState('');

  useEffect(() => {
    if (id) {
      loadProject();
    }
  }, [id]);

  const loadProject = async () => {
    try {
      const project = await projectsApi.get(id!);
      let skills: string[] = [];
      if (project.required_skills) {
        try {
          skills = JSON.parse(project.required_skills);
        } catch {
          skills = [];
        }
      }
      setFormData({
        title: project.title,
        subtitle: project.subtitle || '',
        description: project.description,
        category: project.category,
        cover_image: project.cover_image || '',
        team_size: project.team_size,
        required_skills: skills,
      });
    } catch {
      setError('无法加载项目信息');
    } finally {
      setLoadingProject(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!formData.title.trim()) {
      setError('请输入项目名称');
      return;
    }
    if (formData.description.length < 10) {
      setError('项目详情至少需要10个字符');
      return;
    }

    setLoading(true);

    try {
      const cleanData = {
        title: formData.title.trim(),
        description: formData.description.trim(),
        category: formData.category,
        subtitle: formData.subtitle?.trim() || undefined,
        cover_image: formData.cover_image?.trim() || undefined,
        team_size: formData.team_size || 1,
        required_skills: formData.required_skills?.length ? formData.required_skills : undefined,
      };
      await projectsApi.update(id!, cleanData);
      navigate(`/projects/${id}`);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string | Array<{ msg: string }> } } };
      const detail = error.response?.data?.detail;
      if (typeof detail === 'string') {
        setError(detail);
      } else if (Array.isArray(detail)) {
        setError(detail.map(d => d.msg).join(', '));
      } else {
        setError('更新项目失败，请稍后再试');
      }
    } finally {
      setLoading(false);
    }
  };

  const addSkill = () => {
    if (skillInput.trim() && !formData.required_skills?.includes(skillInput.trim())) {
      setFormData({
        ...formData,
        required_skills: [...(formData.required_skills || []), skillInput.trim()],
      });
      setSkillInput('');
    }
  };

  const removeSkill = (skill: string) => {
    setFormData({
      ...formData,
      required_skills: formData.required_skills?.filter((s) => s !== skill),
    });
  };

  if (loadingProject) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-3xl mx-auto px-4">
          <div className="bg-white rounded-xl shadow-sm p-8 animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
            <div className="space-y-4">
              <div className="h-10 bg-gray-200 rounded"></div>
              <div className="h-10 bg-gray-200 rounded"></div>
              <div className="h-32 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto px-4">
        <div className="bg-white rounded-xl shadow-sm p-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">编辑项目</h1>

          {error && (
            <div className="mb-6 bg-red-50 text-red-600 p-4 rounded-lg">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                项目名称 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                placeholder="给你的项目起个响亮的名字"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                一句话描述
              </label>
              <input
                type="text"
                value={formData.subtitle}
                onChange={(e) => setFormData({ ...formData, subtitle: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                placeholder="用一句话概括你的项目"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                项目分类 <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
              >
                {categories.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                项目详情 <span className="text-red-500">*</span>
              </label>
              <textarea
                required
                rows={8}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                placeholder="详细描述你的项目想法、目标、计划等...（至少10个字符）"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                封面图片链接
              </label>
              <input
                type="url"
                value={formData.cover_image}
                onChange={(e) => setFormData({ ...formData, cover_image: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                placeholder="https://example.com/image.jpg"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                团队规模
              </label>
              <input
                type="number"
                min="1"
                value={formData.team_size}
                onChange={(e) => setFormData({ ...formData, team_size: parseInt(e.target.value) || 1 })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                所需技能
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={skillInput}
                  onChange={(e) => setSkillInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                  placeholder="输入技能标签，回车添加"
                />
                <button
                  type="button"
                  onClick={addSkill}
                  className="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200"
                >
                  添加
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.required_skills?.map((skill) => (
                  <span
                    key={skill}
                    className="inline-flex items-center px-3 py-1 bg-primary-100 text-primary-600 rounded-full text-sm"
                  >
                    {skill}
                    <button
                      type="button"
                      onClick={() => removeSkill(skill)}
                      className="ml-2 hover:text-primary-800"
                    >
                      &times;
                    </button>
                  </span>
                ))}
              </div>
            </div>

            <div className="flex justify-end gap-4 pt-6 border-t">
              <button
                type="button"
                onClick={() => navigate(-1)}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                取消
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
              >
                {loading ? '保存中...' : '保存修改'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
