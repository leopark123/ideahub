import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { investmentsApi, type Investment } from '@/api/investments';
import { useAuthStore } from '@/stores/authStore';

const statusLabels: Record<string, { text: string; color: string }> = {
  pending: { text: '待支付', color: 'bg-yellow-100 text-yellow-600' },
  paid: { text: '已支付', color: 'bg-blue-100 text-blue-600' },
  confirmed: { text: '已确认', color: 'bg-green-100 text-green-600' },
  refunded: { text: '已退款', color: 'bg-gray-100 text-gray-600' },
  cancelled: { text: '已取消', color: 'bg-red-100 text-red-600' },
};

const paymentLabels: Record<string, string> = {
  alipay: '支付宝',
  wechat: '微信',
  bank: '银行卡',
};

export default function MyInvestments() {
  const { user } = useAuthStore();
  const [investments, setInvestments] = useState<Investment[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 10;

  useEffect(() => {
    loadInvestments();
  }, [page]);

  const loadInvestments = async () => {
    setLoading(true);
    try {
      const response = await investmentsApi.getMyInvestments(page, pageSize);
      setInvestments(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Failed to load investments:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const totalPages = Math.ceil(total / pageSize);

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">请先登录</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900">我的投资</h1>
          <Link
            to="/crowdfunding"
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            发现更多项目
          </Link>
        </div>

        {loading ? (
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="bg-white rounded-xl shadow-sm p-6 animate-pulse">
                <div className="flex justify-between">
                  <div className="space-y-2 flex-1">
                    <div className="h-5 bg-gray-200 rounded w-1/3"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                  </div>
                  <div className="h-8 bg-gray-200 rounded w-24"></div>
                </div>
              </div>
            ))}
          </div>
        ) : investments.length > 0 ? (
          <>
            <div className="space-y-4">
              {investments.map((investment) => {
                const status = statusLabels[investment.status] || statusLabels.pending;
                return (
                  <div
                    key={investment.id}
                    className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${status.color}`}>
                            {status.text}
                          </span>
                          {investment.payment_method && (
                            <span className="text-sm text-gray-500">
                              {paymentLabels[investment.payment_method] || investment.payment_method}
                            </span>
                          )}
                        </div>
                        <div className="text-2xl font-bold text-primary-600 mb-1">
                          ¥{investment.amount.toLocaleString()}
                        </div>
                        <div className="text-sm text-gray-500">
                          投资时间：{formatDate(investment.created_at)}
                        </div>
                        {investment.transaction_id && (
                          <div className="text-xs text-gray-400 mt-1">
                            交易号：{investment.transaction_id}
                          </div>
                        )}
                      </div>
                      <Link
                        to={`/crowdfunding`}
                        className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 text-sm"
                      >
                        查看项目
                      </Link>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center items-center gap-2 mt-8">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  上一页
                </button>
                <span className="px-4 py-2 text-gray-600">
                  {page} / {totalPages}
                </span>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  下一页
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <svg
              className="mx-auto h-16 w-16 text-gray-400 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">暂无投资记录</h3>
            <p className="text-gray-500 mb-6">去众筹大厅看看有什么好项目吧</p>
            <Link
              to="/crowdfunding"
              className="inline-flex items-center px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              浏览众筹项目
            </Link>
          </div>
        )}

        {/* Stats Summary */}
        {investments.length > 0 && (
          <div className="mt-8 bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">投资统计</h2>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-primary-600">{total}</div>
                <div className="text-sm text-gray-500">投资次数</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-primary-600">
                  ¥{investments.reduce((sum, inv) => sum + inv.amount, 0).toLocaleString()}
                </div>
                <div className="text-sm text-gray-500">总投资金额</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">
                  {investments.filter((inv) => inv.status === 'confirmed' || inv.status === 'paid').length}
                </div>
                <div className="text-sm text-gray-500">成功投资</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
