import { Link } from 'react-router-dom';
import type { Project } from '@/api/projects';

interface ProjectCardProps {
  project: Project;
}

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

export const ProjectCard = ({ project }: ProjectCardProps) => {
  const status = statusLabels[project.status] || statusLabels.draft;

  return (
    <Link
      to={`/projects/${project.id}`}
      className="block bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow overflow-hidden"
    >
      <div className="relative">
        <img
          src={project.cover_image || 'https://via.placeholder.com/400x200?text=IdeaHub'}
          alt={project.title}
          className="w-full h-48 object-cover"
        />
        <div className="absolute top-3 left-3">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${status.color}`}>
            {status.text}
          </span>
        </div>
        <div className="absolute top-3 right-3">
          <span className="px-2 py-1 bg-white/90 rounded-full text-xs font-medium text-gray-600">
            {categoryLabels[project.category] || project.category}
          </span>
        </div>
      </div>

      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-1">
          {project.title}
        </h3>
        <p className="text-sm text-gray-600 mb-4 line-clamp-2">
          {project.subtitle || project.description}
        </p>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <img
              src={project.owner?.avatar || `https://ui-avatars.com/api/?name=${project.owner?.nickname || 'U'}&background=6366f1&color=fff`}
              alt={project.owner?.nickname || '用户'}
              className="w-6 h-6 rounded-full"
            />
            <span className="text-sm text-gray-600">
              {project.owner?.nickname || '匿名用户'}
            </span>
          </div>

          <div className="flex items-center space-x-3 text-sm text-gray-500">
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              {project.view_count}
            </span>
            <span className="flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
              {project.like_count}
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
};
