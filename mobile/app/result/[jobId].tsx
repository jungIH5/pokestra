import { useEffect, useRef } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useJobStore } from '../../store/jobStore';
import { ProgressBar } from '../../components/ProgressBar';
import { SheetMusicView } from '../../components/SheetMusicView';
import { AudioPlayer } from '../../components/AudioPlayer';

const API_BASE = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';
const POLL_INTERVAL_MS = 2000;

export default function ResultScreen() {
  const { jobId } = useLocalSearchParams<{ jobId: string }>();
  const router = useRouter();
  const { status, current_step, progress, result, error, updateStatus, addToHistory } =
    useJobStore();
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!jobId) return;

    const poll = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/jobs/${jobId}`);
        if (!res.ok) return;
        const data = await res.json();

        updateStatus({
          status: data.status,
          current_step: data.current_step ?? '',
          progress: data.progress ?? 0,
          result: data.result ?? null,
          error: data.error ?? null,
        });

        if (data.status === 'done' && data.result) {
          addToHistory(jobId, data.result);
        }
      } catch {
        // 네트워크 일시 오류는 무시하고 다음 폴링에서 재시도
      }
    };

    poll();
    intervalRef.current = setInterval(poll, POLL_INTERVAL_MS);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [jobId]);

  // 완료 또는 실패 시 폴링 중단
  useEffect(() => {
    if (status === 'done' || status === 'failed') {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }
  }, [status]);

  const isFinished = status === 'done' || status === 'failed';

  return (
    <ScrollView contentContainerStyle={styles.container} bounces={false}>
      {!isFinished && (
        <View style={styles.progressSection}>
          <Text style={styles.stepText}>{current_step || '분석 준비 중...'}</Text>
          <ProgressBar progress={progress} />
          <Text style={styles.progressLabel}>{progress}%</Text>
        </View>
      )}

      {status === 'failed' && (
        <View style={styles.errorSection}>
          <Text style={styles.errorTitle}>오류가 발생했습니다</Text>
          <Text style={styles.errorDetail}>{error ?? '알 수 없는 오류'}</Text>
          <TouchableOpacity style={styles.actionButton} onPress={() => router.back()}>
            <Text style={styles.actionButtonText}>다시 시도</Text>
          </TouchableOpacity>
        </View>
      )}

      {status === 'done' && result && (
        <View style={styles.resultSection}>
          <Text style={styles.sectionTitle}>생성된 악보</Text>
          <SheetMusicView url={result.score_url} />

          <Text style={styles.sectionTitle}>오디오 재생</Text>
          <AudioPlayer url={result.audio_url} />

          {result.image_type === 'general' && result.music_params && (
            <View style={styles.paramsCard}>
              <Text style={styles.sectionTitle}>음악 파라미터</Text>
              <ParamRow label="음계" value={String(result.music_params.scale ?? '-')} />
              <ParamRow label="템포" value={`${result.music_params.tempo ?? '-'} BPM`} />
              <ParamRow label="분위기" value={String(result.music_params.mood ?? '-')} />
              <ParamRow label="음량" value={String(result.music_params.dynamic ?? '-')} />
            </View>
          )}

          {result.image_type === 'sheet_music' && (
            <View style={styles.paramsCard}>
              <Text style={styles.infoText}>악보에서 직접 인식하여 생성했습니다</Text>
            </View>
          )}

          <TouchableOpacity
            style={[styles.actionButton, styles.actionButtonPrimary]}
            onPress={() => router.push('/')}
          >
            <Text style={styles.actionButtonText}>새 사진으로 만들기</Text>
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
}

function ParamRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.paramRow}>
      <Text style={styles.paramLabel}>{label}</Text>
      <Text style={styles.paramValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 24, backgroundColor: '#fff', flexGrow: 1 },

  progressSection: { alignItems: 'center', marginTop: 64, gap: 12 },
  stepText: { fontSize: 16, color: '#444', textAlign: 'center' },
  progressLabel: { fontSize: 14, color: '#888' },

  errorSection: { alignItems: 'center', marginTop: 64, gap: 16 },
  errorTitle: { fontSize: 20, fontWeight: 'bold', color: '#b00020' },
  errorDetail: { fontSize: 14, color: '#666', textAlign: 'center', lineHeight: 20 },

  resultSection: { gap: 8 },
  sectionTitle: { fontSize: 17, fontWeight: '700', color: '#222', marginTop: 20 },

  paramsCard: {
    backgroundColor: '#f5f0ff',
    borderRadius: 12,
    padding: 16,
    marginTop: 4,
    gap: 8,
  },
  paramRow: { flexDirection: 'row', justifyContent: 'space-between' },
  paramLabel: { fontSize: 14, color: '#555' },
  paramValue: { fontSize: 14, fontWeight: '600', color: '#333' },
  infoText: { fontSize: 14, color: '#555', textAlign: 'center' },

  actionButton: {
    backgroundColor: '#b00020',
    borderRadius: 14,
    padding: 18,
    alignItems: 'center',
    marginTop: 8,
  },
  actionButtonPrimary: { backgroundColor: '#6200ee', marginTop: 24 },
  actionButtonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
});
