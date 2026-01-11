import { Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from '@/components/layout/Navbar';
import { useAuthStore } from '@/stores/authStore';
import Home from '@/pages/Home';
import Login from '@/pages/auth/Login';
import Register from '@/pages/auth/Register';
import CreateProject from '@/pages/projects/CreateProject';
import ProjectDetail from '@/pages/projects/ProjectDetail';
import ProjectEdit from '@/pages/projects/ProjectEdit';
import CreateCrowdfunding from '@/pages/projects/CreateCrowdfunding';
import Partners from '@/pages/Partners';
import CrowdfundingPage from '@/pages/Crowdfunding';
import Profile from '@/pages/Profile';
import MyProjects from '@/pages/MyProjects';
import MyInvestments from '@/pages/MyInvestments';
import Messages from '@/pages/Messages';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }

  return <>{children}</>;
};

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/auth/login" element={<Login />} />
          <Route path="/auth/register" element={<Register />} />
          <Route path="/projects/:id" element={<ProjectDetail />} />
          <Route
            path="/projects/:id/edit"
            element={
              <ProtectedRoute>
                <ProjectEdit />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:id/crowdfunding/new"
            element={
              <ProtectedRoute>
                <CreateCrowdfunding />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/new"
            element={
              <ProtectedRoute>
                <CreateProject />
              </ProtectedRoute>
            }
          />
          <Route path="/partners" element={<Partners />} />
          <Route path="/crowdfunding" element={<CrowdfundingPage />} />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />
          <Route
            path="/my-projects"
            element={
              <ProtectedRoute>
                <MyProjects />
              </ProtectedRoute>
            }
          />
          <Route
            path="/my-investments"
            element={
              <ProtectedRoute>
                <MyInvestments />
              </ProtectedRoute>
            }
          />
          <Route
            path="/messages"
            element={
              <ProtectedRoute>
                <Messages />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
    </div>
  );
}

export default App;
