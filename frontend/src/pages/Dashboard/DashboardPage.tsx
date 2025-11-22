/**
 * Dashboard page - main page after login.
 */
import { useAuthStore } from '@/stores/authStore'
import { useNavigate } from 'react-router-dom'

export default function DashboardPage() {
  const user = useAuthStore((state) => state.user)
  const logout = useAuthStore((state) => state.logout)
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Fitness Trainer Dashboard</h1>
        <button onClick={handleLogout} style={{ padding: '10px 20px' }}>
          Logout
        </button>
      </div>

      <div style={{ marginTop: '30px' }}>
        <h2>Welcome, {user?.username}!</h2>
        <p>Email: {user?.email}</p>

        <div style={{ marginTop: '40px' }}>
          <h3>Quick Stats</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginTop: '20px' }}>
            <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
              <h4>Workouts This Week</h4>
              <p style={{ fontSize: '2em', margin: '10px 0' }}>0</p>
            </div>
            <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
              <h4>Personal Records</h4>
              <p style={{ fontSize: '2em', margin: '10px 0' }}>0</p>
            </div>
            <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
              <h4>Current Streak</h4>
              <p style={{ fontSize: '2em', margin: '10px 0' }}>0 days</p>
            </div>
          </div>
        </div>

        <div style={{ marginTop: '40px' }}>
          <h3>Getting Started</h3>
          <p>Start building your fitness tracking application! This is a placeholder dashboard.</p>
          <ul>
            <li>Create your first workout program</li>
            <li>Log your first workout session</li>
            <li>Track your progress over time</li>
            <li>View analytics and charts</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
