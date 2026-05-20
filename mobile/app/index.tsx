import { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useRouter } from 'expo-router';
import { useJobStore } from '../store/jobStore';

const API_BASE = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';

export default function HomeScreen() {
  const router = useRouter();
  const { setJob } = useJobStore();
  const [uploading, setUploading] = useState(false);

  const pickAndUpload = async (useCamera: boolean) => {
    const perm = useCamera
      ? await ImagePicker.requestCameraPermissionsAsync()
      : await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (!perm.granted) {
      Alert.alert('권한 필요', '사진 접근 권한이 필요합니다.');
      return;
    }

    const pickerResult = useCamera
      ? await ImagePicker.launchCameraAsync({ quality: 0.85, allowsEditing: false })
      : await ImagePicker.launchImageLibraryAsync({ quality: 0.85, mediaTypes: ImagePicker.MediaTypeOptions.Images });

    if (pickerResult.canceled || !pickerResult.assets[0]) return;

    setUploading(true);
    try {
      const asset = pickerResult.assets[0];
      const form = new FormData();
      form.append('image', {
        uri: asset.uri,
        type: asset.mimeType ?? 'image/jpeg',
        name: 'photo.jpg',
      } as unknown as Blob);

      const res = await fetch(`${API_BASE}/api/analyze/`, {
        method: 'POST',
        body: form,
      });

      if (!res.ok) {
        const body = await res.text();
        throw new Error(`서버 오류 ${res.status}: ${body}`);
      }

      const { job_id } = await res.json();
      setJob(job_id);
      router.push(`/result/${job_id}`);
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : '알 수 없는 오류가 발생했습니다.';
      Alert.alert('업로드 실패', message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Photo Maestro</Text>
      <Text style={styles.subtitle}>사진으로 음악을 만들어 보세요</Text>

      {uploading ? (
        <View style={styles.loadingBox}>
          <ActivityIndicator size="large" color="#6200ee" />
          <Text style={styles.loadingText}>업로드 중...</Text>
        </View>
      ) : (
        <View style={styles.buttonGroup}>
          <TouchableOpacity
            style={styles.button}
            onPress={() => pickAndUpload(true)}
          >
            <Text style={styles.buttonText}>카메라로 촬영</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, styles.buttonSecondary]}
            onPress={() => pickAndUpload(false)}
          >
            <Text style={styles.buttonText}>갤러리에서 선택</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, styles.buttonOutline]}
            onPress={() => router.push('/history')}
          >
            <Text style={[styles.buttonText, styles.buttonTextOutline]}>
              히스토리
            </Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    backgroundColor: '#fff',
  },
  title: { fontSize: 34, fontWeight: 'bold', color: '#6200ee', marginBottom: 8 },
  subtitle: { fontSize: 16, color: '#666', marginBottom: 56 },
  loadingBox: { alignItems: 'center', gap: 12 },
  loadingText: { fontSize: 14, color: '#666' },
  buttonGroup: { width: '100%', gap: 12 },
  button: {
    backgroundColor: '#6200ee',
    borderRadius: 14,
    padding: 18,
    alignItems: 'center',
  },
  buttonSecondary: { backgroundColor: '#03dac6' },
  buttonOutline: {
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: '#6200ee',
  },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  buttonTextOutline: { color: '#6200ee' },
});
