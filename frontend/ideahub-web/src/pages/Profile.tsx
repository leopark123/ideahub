import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { usersApi, type User } from '@/api/users';
import { projectsApi } from '@/api/projects';
import { investmentsApi } from '@/api/investments';

const skillOptions = [
  '技术开发',
  '产品设计',
  'UI/UX',
  '市场营销',
  '运营管理',
  '财务投资',
  '法务咨询',
  '人力资源',
];

export default function Profile() {
  const { user, setUser } = useAuthStore();
  const [profile, setProfile] = useState<User | null>(null);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ projects: 0, investments: 0 });
  const [formData, setFormData] = useState({
    nickname: '',
    bio: '',
    skills: [] as string[],
    experience: '',
  });
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    if (user) {
      loadProfile();
      loadStats();
    }
  }, [user]);

  const loadProfile = async () => {
    try {
      const data = await usersApi.getMe();
      setProfile(data);
      let skills: string[] = [];
      if (data.skills) {
        try {
          skills = JSON.parse(data.skills);
        } catch {
          skills = [];
        }
      }
      setFormData({
        nickname: data.nickname || '',
        bio: data.bio || '',
        skills: skills,
        experience: data.experience || '',
      });
    } catch (error) {
      console.error('Failed to load profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const [projectsRes, investmentsRes] = await Promise.all([
        projectsApi.list({ page_size: 1 }),
        investmentsApi.getMyInvestments(1, 1),
      ]);
      setStats({
        projects: projectsRes.total,
        investments: investmentsRes.total,
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleSkillToggle = (skill: string) => {
    setFormData((prev) => ({
      ...prev,
      skills: prev.skills.includes(skill)
        ? prev.skills.filter((s) => s !== skill)
        : [...prev.skills, skill],
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage({ type: '', text: '' });

    try {
      const updatedUser = await usersApi.updateMe({
        nickname: formData.nickname,
        bio: formData.bio,
        skills: formData.skills,
        experience: formData.experience,
      });

      setProfile(updatedUser);
      setUser({
        id: updatedUser.id,
        email: updatedUser.email,
        nickname: updatedUser.nickname || updatedUser.email.split('@')[0],
        avatar: updatedUser.avatar || undefined,
        role: updatedUser.role,
      });

      setMessage({ type: 'success', text: '保存成功' });
      setEditing(false);
    } catch (error) {
      console.error('Failed to update profile:', error);
      setMessage({ type: 'error', text: '保存失败，请稍后再试' });
    } finally {
      setSaving(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">请先登录</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-3xl mx-auto px-4">
          <div className="bg-white rounded-xl shadow-sm overflow-hidden animate-pulse">
            <div className="bg-gray-200 h-32"></div>
            <div className="px-6 pb-6">
              <div className="flex items-end -mt-16 mb-4">
                <div className="w-24 h-24 rounded-full bg-gray-300 border-4 border-white"></div>
                <div className="ml-4 mb-2 space-y-2">
                  <div className="h-6 bg-gray-200 rounded w-32"></div>
                  <div className="h-4 bg-gray-200 rounded w-48"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const displaySkills = profile?.skills ? (() => {
    try {
      return JSON.parse(profile.skills);
    } catch {
      return [];
    }
  })() : [];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto px-4">
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="bg-gradient-to-r from-primary-600 to-primary-800 h-32"></div>

          <div className="px-6 pb-6">
            <div className="flex items-end -mt-16 mb-4">
              <img
                src={user.avatar || `https://ui-avatars.com/api/?name=${user.nickname}&background=6366f1&color=fff&size=128`}
                alt={user.nickname}
                className="w-24 h-24 rounded-full border-4 border-white shadow-lg"
              />
              <div className="ml-4 mb-2">
                <h1 className="text-2xl font-bold text-gray-900">{user.nickname}</h1>
                <p className="text-gray-500">{user.email}</p>
              </div>
            </div>

            {message.text && (
              <div
                className={`mb-4 p-3 rounded-lg text-sm ${
                  message.type === 'success'
                    ? 'bg-green-50 text-green-600'
                    : 'bg-red-50 text-red-600'
                }`}
              >
                {message.text}
              </div>
            )}

            {editing ? (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    昵称
                  </label>
                  <input
                    type="text"
                    value={formData.nickname}
                    onChange={(e) =>
                      setFormData({ ...formData, nickname: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    placeholder="您的昵称"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    个人简介
                  </label>
                  <textarea
                    value={formData.bio}
                    onChange={(e) =>
                      setFormData({ ...formData, bio: e.target.value })
                    }
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    placeholder="介绍一下自己..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    技能标签
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {skillOptions.map((skill) => (
                      <button
                        key={skill}
                        type="button"
                        onClick={() => handleSkillToggle(skill)}
                        className={`px-3 py-1 rounded-full text-sm transition-colors ${
                          formData.skills.includes(skill)
                            ? 'bg-primary-600 text-white'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}
                      >
                        {skill}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    工作经历
                  </label>
                  <textarea
                    value={formData.experience}
                    onChange={(e) =>
                      setFormData({ ...formData, experience: e.target.value })
                    }
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    placeholder="描述您的工作经历和专业背景..."
                  />
                </div>

                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setEditing(false)}
                    className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    取消
                  </button>
                  <button
                    type="submit"
                    disabled={saving}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
                  >
                    {saving ? '保存中...' : '保存'}
                  </button>
                </div>
              </form>
            ) : (
              <div>
                <div className="flex justify-end mb-4">
                  <button
                    onClick={() => setEditing(true)}
                    className="px-4 py-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                  >
                    编辑资料
                  </button>
                </div>

                {/* Bio Section */}
                {profile?.bio && (
                  <div className="mb-6">
                    <h3 className="font-medium text-gray-900 mb-2">个人简介</h3>
                    <p className="text-gray-600">{profile.bio}</p>
                  </div>
                )}

                {/* Skills Section */}
                {displaySkills.length > 0 && (
                  <div className="mb-6">
                    <h3 className="font-medium text-gray-900 mb-2">技能标签</h3>
                    <div className="flex flex-wrap gap-2">
                      {displaySkills.map((skill: string) => (
                        <span
                          key={skill}
                          className="px-3 py-1 bg-primary-100 text-primary-600 rounded-full text-sm"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Experience Section */}
                {profile?.experience && (
                  <div className="mb-6">
                    <h3 className="font-medium text-gray-900 mb-2">工作经历</h3>
                    <p className="text-gray-600 whitespace-pre-wrap">{profile.experience}</p>
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="font-medium text-gray-900 mb-2">账号信息</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500">邮箱</span>
                        <span className="text-gray-900">{user.email}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">角色</span>
                        <span className="text-gray-900">
                          {user.role === 'admin' ? '管理员' : '普通用户'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">注册时间</span>
                        <span className="text-gray-900">
                          {profile?.created_at
                            ? new Date(profile.created_at).toLocaleDateString('zh-CN')
                            : '-'}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="font-medium text-gray-900 mb-2">统计数据</h3>
                    <div className="grid grid-cols-2 gap-4 text-center">
                      <Link to="/my-projects" className="hover:bg-gray-100 rounded-lg p-2 transition-colors">
                        <div className="text-2xl font-bold text-primary-600">{stats.projects}</div>
                        <div className="text-xs text-gray-500">发布项目</div>
                      </Link>
                      <Link to="/my-investments" className="hover:bg-gray-100 rounded-lg p-2 transition-colors">
                        <div className="text-2xl font-bold text-primary-600">{stats.investments}</div>
                        <div className="text-xs text-gray-500">参与投资</div>
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
