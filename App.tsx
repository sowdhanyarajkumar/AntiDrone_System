import React, { useState, useEffect, useCallback } from 'react';
import { MainLayout } from './layouts/MainLayout';
import { NavTab } from './components/Sidebar';
import { useWebSocket } from './hooks/useWebSocket';
import { api } from './services/api';

import { DashboardPage } from './pages/DashboardPage';
import { LiveMonitorPage } from './pages/LiveMonitorPage';
import { AIDetectionPage } from './pages/AIDetectionPage';
import { TrackingPage } from './pages/TrackingPage';
import { EnvironmentPage } from './pages/EnvironmentPage';
import { SystemHealthPage } from './pages/SystemHealthPage';
import { HighAltitudeAnalysisPage } from './pages/HighAltitudeAnalysisPage';
import { SessionsPage } from './pages/SessionsPage';
import { EventsPage } from './pages/EventsPage';
import { SettingsPage } from './pages/SettingsPage';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<NavTab>('dashboard');
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [aiMode, setAiMode] = useState<string>('SIMULATED');

  // Real-time WebSocket hook with 60-second rolling history buffer
  const {
    status: connectionStatus,
    latestData,
    history,
    recentEvents,
    lastHeartbeat,
  } = useWebSocket(60);

  const refreshStatus = useCallback(async () => {
    try {
      const status = await api.getSystemStatus();
      if (status) {
        setIsSimulating(status.is_simulating);
        setIsPaused(status.is_paused);
        setSessionId(status.session_id !== 'WAITING FOR SESSION' ? status.session_id : '');
        setAiMode(status.ai_mode);
      }
    } catch (e) {
      console.error(e);
    }
  }, []);

  useEffect(() => {
    refreshStatus();
    const interval = setInterval(refreshStatus, 3000);
    return () => clearInterval(interval);
  }, [refreshStatus]);

  // Update session ID & status when telemetry packets arrive
  useEffect(() => {
    if (latestData && latestData.session_id) {
      if (latestData.session_id !== 'STANDBY') {
        setSessionId(latestData.session_id);
        setIsSimulating(true);
      }
    }
  }, [latestData]);

  return (
    <MainLayout
      currentTab={currentTab}
      onSelectTab={setCurrentTab}
      connectionStatus={connectionStatus}
      sessionId={sessionId}
      isSimulating={isSimulating}
      aiMode={aiMode}
      lastHeartbeat={lastHeartbeat}
      eventCount={recentEvents.length}
    >
      {currentTab === 'dashboard' && (
        <DashboardPage
          telemetry={latestData}
          history={history}
          isSimulating={isSimulating}
          isPaused={isPaused}
          onRefreshStatus={refreshStatus}
        />
      )}

      {currentTab === 'monitor' && (
        <LiveMonitorPage
          telemetry={latestData}
          events={recentEvents}
        />
      )}

      {currentTab === 'detection' && (
        <AIDetectionPage
          currentAiMode={aiMode}
          fps={latestData?.computer.fps || 24}
          latency={latestData?.computer.ai_latency || 35}
        />
      )}

      {currentTab === 'tracking' && (
        <TrackingPage
          tracking={latestData?.tracking || null}
        />
      )}

      {currentTab === 'environment' && (
        <EnvironmentPage
          environment={latestData?.environment || null}
          history={history}
        />
      )}

      {currentTab === 'health' && (
        <SystemHealthPage
          telemetry={latestData}
        />
      )}

      {currentTab === 'analysis' && (
        <HighAltitudeAnalysisPage />
      )}

      {currentTab === 'sessions' && (
        <SessionsPage />
      )}

      {currentTab === 'events' && (
        <EventsPage liveEvents={recentEvents} />
      )}

      {currentTab === 'settings' && (
        <SettingsPage />
      )}
    </MainLayout>
  );
};

export default App;
