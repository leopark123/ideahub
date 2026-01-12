import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { projectsApi, type Project } from '@/api/projects';
import { crowdfundingApi, type Crowdfunding } from '@/api/crowdfunding';
import { messagesApi } from '@/api/messages';
import { investmentsApi } from '@/api/investments';
import { partnershipsApi, type Partnership, type PartnershipRole, roleLabels } from '@/api/partnerships';
import { useAuthStore } from '@/stores/authStore';

const categoryLabels: Record<string, string> = {
  tech: '科技',
  art: '艺术',
  education: '教育',
  health: '健康',
  social: '社会公益',
  entertainment: '娱乐',
  finance: '金融',
  other: '其他',
};

const statusLabels: Record<string, { text: string; color: string }> = {
  draft: { text: '草稿', color: 'bg-gray-100 text-gray-600' },
  pending: { text: '审核中', color: 'bg-yellow-100 text-yellow-600' },
  active: { text: '已发布', color: 'bg-green-100 text-green-600' },
  funding: { text: '众筹中', color: 'bg-blue-100 text-blue-600' },
  funded: { text: '众筹成功', color: 'bg-purple-100 text-purple-600' },
  failed: { text: '众筹失败', color: 'bg-red-100 text-red-600' },
  completed: { text: '已完成', color: 'bg-gray-100 text-gray-600' },
};

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const { isAuthenticated, user } = useAuthStore();
  const [project, setProject] = useState<Project | null>(null);
  const [crowdfunding, setCrowdfunding] = useState<Crowdfunding | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showContactModal, setShowContactModal] = useState(false);
  const [contactMessage, setContactMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [showInvestModal, setShowInvestModal] = useState(false);
  const [investAmount, setInvestAmount] = useState('');
  const [investing, setInvesting] = useState(false);
  const [showApplyModal, setShowApplyModal] = useState(false);
  const [applyData, setApplyData] = useState({
    role: 'member' as PartnershipRole,
    position: '',
    message: '',
  });
  const [applying, setApplying] = useState(false);
  const [myPartnership, setMyPartnership] = useState<Partnership | null>(null);
  const [pendingApplications, setPendingApplications] = useState<Partnership[]>([]);
  const [processingId, setProcessingId] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadProject();
      loadCrowdfunding();
    }
  }, [id]);

  useEffect(() => {
    if (id && isAuthenticated) {
      loadMyPartnership();
    }
  }, [id, isAuthenticated]);

  useEffect(() => {
    if (id && isAuthenticated && project && user?.id === project.owner_id) {
      loadPendingApplications();
    }
  }, [id, isAuthenticated, project, user]);

  const loadProject = async () => {
    try {
      const data = await projectsApi.get(id!);
      setProject(data);
    } catch (err) {
      setError('项目不存在或已被删除');
    } finally {
      setLoading(false);
    }
  };

  const loadCrowdfunding = async () => {
    try {
      const data = await crowdfundingApi.getByProject(id!);
      setCrowdfunding(data);
    } catch {
      // No crowdfunding for this project
    }
  };

  const loadMyPartnership = async () => {
    try {
      const data = await partnershipsApi.getMyApplications(1, 100);
      const found = data.items.find(p => p.project_id === id);
      setMyPartnership(found || null);
    } catch {
      // Ignore
    }
  };

  const loadPendingApplications = async () => {
    try {
      const data = await partnershipsApi.getProjectPartnerships(id!, 'pending', 1, 100);
      setPendingApplications(data.items);
    } catch {
      // Ignore
    }
  };

  const handleApprove = async (partnershipId: string) => {
    setProcessingId(partnershipId);
    try {
      await partnershipsApi.approve(partnershipId);
      setPendingApplications(prev => prev.filter(p => p.id !== partnershipId));
      alert('已批准该申请');
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      alert(error.response?.data?.detail || '操作失败');
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (partnershipId: string) => {
    setProcessingId(partnershipId);
    try {
      await partnershipsApi.reject(partnershipId);
      setPendingApplications(prev => prev.filter(p => p.id !== partnershipId));
      alert('已拒绝该申请');
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      alert(error.response?.data?.detail || '操作失败');
    } finally {
      setProcessingId(null);
    }
  };

  const handleApply = async () => {
    if (!id) return;
    setApplying(true);
    try {
      const partnership = await partnershipsApi.apply({
        project_id: id,
        role: applyData.role,
        position: applyData.position || undefined,
        application_message: applyData.message || undefined,
      });
      setMyPartnership(partnership);
      setShowApplyModal(false);
      setApplyData({ role: 'member', position: '', message: '' });
      alert('申请已提交，等待项目方审核');
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      alert(error.response?.data?.detail || '申请失败，请稍后再试');
    } finally {
      setApplying(false);
    }
  };

  const handleContact = async () => {
    if (!contactMessage.trim() || !project) return;
    setSending(true);
    try {
      await messagesApi.sendMessage({
        receiver_id: project.owner_id,
        content: contactMessage.trim(),
        project_id: project.id,
      });
      setShowContactModal(false);
      setContactMessage('');
      alert('消息已发送！');
    } catch (err) {
      alert('发送失败，请稍后再试');
    } finally {
      setSending(false);
    }
  };

  const handleInvest = async () => {
    if (!crowdfunding || !investAmount) return;
    const amount = parseFloat(investAmount);
    if (isNaN(amount) || amount < crowdfunding.min_investment) {
      alert(`最低投资金额为 ${crowdfunding.min_investment} 元`);
      return;
    }
    setInvesting(true);
    try {
      const investment = await investmentsApi.create({
        crowdfunding_id: crowdfunding.id,
        amount: amount,
        payment_method: 'alipay',
      });
      // 模拟支付成功
      await investmentsApi.confirm(investment.id, `TXN_${Date.now()}`);
      setShowInvestModal(false);
      setInvestAmount('');
      alert('投资成功！感谢您的支持！');
      // 刷新众筹数据
      loadCrowdfunding();
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      alert(error.response?.data?.detail || '投资失败，请稍后再试');
    } finally {
      setInvesting(false);
    }
  };

  const handleLike = async () => {
    if (!project) return;
    try {
      const updated = await projectsApi.like(project.id);
      setProject(updated);
    } catch (err) {
      console.error('Failed to like project:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-white rounded-xl shadow-sm p-8 animate-pulse">
            <div className="h-64 bg-gray-200 rounded-lg mb-6"></div>
            <div className="h-8 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-8"></div>
            <div className="space-y-3">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded w-4/5"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <div className="bg-white rounded-xl shadow-sm p-8">
            <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="text-xl font-medium text-gray-900 mb-2">{error || '项目未找到'}</h2>
            <Link to="/" className="text-primary-600 hover:text-primary-700">
              返回首页
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const status = statusLabels[project.status] || statusLabels.draft;
  const isOwner = user?.id === project.owner_id;
  const skills = project.required_skills ? JSON.parse(project.required_skills) : [];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          {/* Cover Image */}
          <img
            src={project.cover_image || 'https://via.placeholder.com/800x400?text=IdeaHub'}
            alt={project.title}
            className="w-full h-64 md:h-80 object-cover"
          />

          {/* Content */}
          <div className="p-6 md:p-8">
            {/* Header */}
            <div className="flex items-start justify-between mb-6">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${status.color}`}>
                    {status.text}
                  </span>
                  <span className="px-2 py-1 bg-gray-100 rounded-full text-xs font-medium text-gray-600">
                    {categoryLabels[project.category] || project.category}
                  </span>
                </div>
                <h1 className="text-2xl md:text-3xl font-bold text-gray-900">{project.title}</h1>
                {project.subtitle && (
                  <p className="text-lg text-gray-600 mt-2">{project.subtitle}</p>
                )}
              </div>

              {isOwner && (
                <div className="flex gap-2">
                  {!crowdfunding && (
                    <Link
                      to={`/projects/${project.id}/crowdfunding/new`}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                    >
                      发起众筹
                    </Link>
                  )}
                  <Link
                    to={`/projects/${project.id}/edit`}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                  >
                    编辑项目
                  </Link>
                </div>
              )}
            </div>

            {/* Owner Info */}
            <div className="flex items-center justify-between py-4 border-y border-gray-200 mb-6">
              <div className="flex items-center space-x-3">
                <img
                  src={project.owner?.avatar || `https://ui-avatars.com/api/?name=${project.owner?.nickname || 'U'}&background=6366f1&color=fff`}
                  alt={project.owner?.nickname || '用户'}
                  className="w-10 h-10 rounded-full"
                />
                <div>
                  <div className="font-medium text-gray-900">
                    {project.owner?.nickname || '匿名用户'}
                  </div>
                  <div className="text-sm text-gray-500">项目发起人</div>
                </div>
              </div>

              <div className="flex items-center space-x-6 text-sm text-gray-500">
                <span className="flex items-center">
                  <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  {project.view_count} 浏览
                </span>
                <span className="flex items-center">
                  <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                  {project.like_count} 喜欢
                </span>
              </div>
            </div>

            {/* Description */}
            <div className="prose max-w-none mb-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">项目详情</h2>
              <div className="text-gray-700 whitespace-pre-wrap">{project.description}</div>
            </div>

            {/* Skills */}
            {skills.length > 0 && (
              <div className="mb-8">
                <h2 className="text-lg font-semibold text-gray-900 mb-3">所需技能</h2>
                <div className="flex flex-wrap gap-2">
                  {skills.map((skill: string) => (
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

            {/* Team Info */}
            <div className="mb-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">团队规模</h2>
              <p className="text-gray-700">计划团队人数: {project.team_size} 人</p>
            </div>

            {/* Pending Applications - Only visible to owner */}
            {isOwner && pendingApplications.length > 0 && (
              <div className="mb-8 p-6 bg-yellow-50 border border-yellow-200 rounded-xl">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                  </svg>
                  待审批申请 ({pendingApplications.length})
                </h2>
                <div className="space-y-4">
                  {pendingApplications.map((application) => (
                    <div key={application.id} className="bg-white p-4 rounded-lg shadow-sm">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center space-x-3">
                          <img
                            src={application.user?.avatar || `https://ui-avatars.com/api/?name=${application.user?.nickname || 'U'}&background=6366f1&color=fff`}
                            alt={application.user?.nickname || '用户'}
                            className="w-10 h-10 rounded-full"
                          />
                          <div>
                            <div className="font-medium text-gray-900">
                              {application.user?.nickname || '匿名用户'}
                            </div>
                            <div className="text-sm text-gray-500">
                              申请角色: {roleLabels[application.role] || application.role}
                              {application.position && ` · 期望职位: ${application.position}`}
                            </div>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleApprove(application.id)}
                            disabled={processingId === application.id}
                            className="px-3 py-1 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                          >
                            {processingId === application.id ? '处理中...' : '批准'}
                          </button>
                          <button
                            onClick={() => handleReject(application.id)}
                            disabled={processingId === application.id}
                            className="px-3 py-1 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                          >
                            拒绝
                          </button>
                        </div>
                      </div>
                      {application.application_message && (
                        <div className="mt-3 text-sm text-gray-600 bg-gray-50 p-3 rounded">
                          <span className="font-medium">申请说明：</span>
                          {application.application_message}
                        </div>
                      )}
                      <div className="mt-2 text-xs text-gray-400">
                        申请时间: {new Date(application.created_at).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Crowdfunding Info */}
            {crowdfunding && crowdfunding.status === 'active' && (
              <div className="mb-8 p-6 bg-gradient-to-r from-primary-50 to-blue-50 rounded-xl">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">众筹进行中</h2>
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-600">已筹集</span>
                    <span className="font-semibold text-primary-600">
                      {((crowdfunding.current_amount / crowdfunding.target_amount) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-primary-600 h-3 rounded-full transition-all"
                      style={{ width: `${Math.min((crowdfunding.current_amount / crowdfunding.target_amount) * 100, 100)}%` }}
                    ></div>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-xl font-bold text-gray-900">¥{crowdfunding.current_amount.toLocaleString()}</div>
                    <div className="text-xs text-gray-500">已筹金额</div>
                  </div>
                  <div>
                    <div className="text-xl font-bold text-gray-900">{crowdfunding.investor_count}</div>
                    <div className="text-xs text-gray-500">支持人数</div>
                  </div>
                  <div>
                    <div className="text-xl font-bold text-gray-900">¥{crowdfunding.target_amount.toLocaleString()}</div>
                    <div className="text-xs text-gray-500">目标金额</div>
                  </div>
                </div>
                <div className="mt-4 text-center text-sm text-gray-500">
                  最低投资: ¥{crowdfunding.min_investment}
                </div>
                {isAuthenticated && !isOwner && (
                  <button
                    onClick={() => setShowInvestModal(true)}
                    className="mt-4 w-full py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium"
                  >
                    立即投资
                  </button>
                )}
              </div>
            )}

            {/* Actions */}
            <div className="flex flex-wrap items-center gap-4 pt-6 border-t border-gray-200">
              <button
                onClick={handleLike}
                className="flex items-center px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
                喜欢
              </button>

              {isAuthenticated && !isOwner && (
                <>
                  <button
                    onClick={() => setShowContactModal(true)}
                    className="flex items-center px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    联系发起人
                  </button>
                  {myPartnership ? (
                    <span className={`flex items-center px-6 py-3 rounded-lg ${
                      myPartnership.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                      myPartnership.status === 'approved' ? 'bg-green-100 text-green-700' :
                      myPartnership.status === 'rejected' ? 'bg-red-100 text-red-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                      </svg>
                      {myPartnership.status === 'pending' ? '申请中' :
                       myPartnership.status === 'approved' ? '已加入团队' :
                       myPartnership.status === 'rejected' ? '申请被拒绝' : '已退出'}
                    </span>
                  ) : (
                    <button
                      onClick={() => setShowApplyModal(true)}
                      className="flex items-center px-6 py-3 border border-primary-600 text-primary-600 rounded-lg hover:bg-primary-50"
                    >
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                      </svg>
                      申请加入
                    </button>
                  )}
                </>
              )}

              <button className="flex items-center px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                </svg>
                分享
              </button>
            </div>
          </div>
        </div>

        {/* Contact Modal */}
        {showContactModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl max-w-md w-full p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">联系项目发起人</h3>
                <button
                  onClick={() => setShowContactModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                向 {project.owner?.nickname || '项目发起人'} 发送消息，关于项目「{project.title}」
              </p>
              <textarea
                value={contactMessage}
                onChange={(e) => setContactMessage(e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-primary-500 focus:border-primary-500 mb-4"
                placeholder="介绍一下自己，说明想要合作的意向..."
              />
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setShowContactModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  取消
                </button>
                <button
                  onClick={handleContact}
                  disabled={!contactMessage.trim() || sending}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  {sending ? '发送中...' : '发送消息'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Invest Modal */}
        {showInvestModal && crowdfunding && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl max-w-md w-full p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">投资项目</h3>
                <button
                  onClick={() => setShowInvestModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600 mb-2">投资项目：{project.title}</div>
                <div className="text-sm text-gray-600">最低投资：¥{crowdfunding.min_investment}</div>
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  投资金额（元）
                </label>
                <input
                  type="number"
                  value={investAmount}
                  onChange={(e) => setInvestAmount(e.target.value)}
                  min={crowdfunding.min_investment}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder={`最低 ${crowdfunding.min_investment} 元`}
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  支付方式
                </label>
                <div className="grid grid-cols-3 gap-2">
                  <button className="p-3 border-2 border-primary-600 rounded-lg text-center bg-primary-50">
                    <span className="text-sm font-medium text-primary-600">支付宝</span>
                  </button>
                  <button className="p-3 border border-gray-200 rounded-lg text-center opacity-50 cursor-not-allowed">
                    <span className="text-sm text-gray-400">微信</span>
                  </button>
                  <button className="p-3 border border-gray-200 rounded-lg text-center opacity-50 cursor-not-allowed">
                    <span className="text-sm text-gray-400">银行卡</span>
                  </button>
                </div>
              </div>
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setShowInvestModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  取消
                </button>
                <button
                  onClick={handleInvest}
                  disabled={!investAmount || investing}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  {investing ? '处理中...' : '确认投资'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Apply Modal */}
        {showApplyModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl max-w-md w-full p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">申请加入项目</h3>
                <button
                  onClick={() => setShowApplyModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                申请加入「{project.title}」团队
              </p>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  期望角色
                </label>
                <select
                  value={applyData.role}
                  onChange={(e) => setApplyData({ ...applyData, role: e.target.value as PartnershipRole })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="member">{roleLabels.member}</option>
                  <option value="partner">{roleLabels.partner}</option>
                  <option value="advisor">{roleLabels.advisor}</option>
                  <option value="co_founder">{roleLabels.co_founder}</option>
                </select>
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  期望职位（选填）
                </label>
                <input
                  type="text"
                  value={applyData.position}
                  onChange={(e) => setApplyData({ ...applyData, position: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="如：技术负责人、产品经理..."
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  申请说明
                </label>
                <textarea
                  value={applyData.message}
                  onChange={(e) => setApplyData({ ...applyData, message: e.target.value })}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="介绍一下自己的背景、技能，以及为什么想加入这个项目..."
                />
              </div>
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setShowApplyModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  取消
                </button>
                <button
                  onClick={handleApply}
                  disabled={applying}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  {applying ? '提交中...' : '提交申请'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
