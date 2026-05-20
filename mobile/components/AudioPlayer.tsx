import { useState, useEffect, useRef } from 'react';
import { View, TouchableOpacity, Text, StyleSheet } from 'react-native';
import { Audio } from 'expo-av';

interface Props {
  url: string;
}

export function AudioPlayer({ url }: Props) {
  const soundRef = useRef<Audio.Sound | null>(null);
  const [playing, setPlaying] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    Audio.setAudioModeAsync({ playsInSilentModeIOS: true });
    return () => {
      soundRef.current?.unloadAsync();
    };
  }, []);

  const togglePlay = async () => {
    if (loading) return;

    if (soundRef.current) {
      if (playing) {
        await soundRef.current.pauseAsync();
        setPlaying(false);
      } else {
        await soundRef.current.playAsync();
        setPlaying(true);
      }
      return;
    }

    setLoading(true);
    try {
      const { sound } = await Audio.Sound.createAsync(
        { uri: url },
        { shouldPlay: true },
        (status) => {
          if (status.isLoaded && status.didJustFinish) {
            setPlaying(false);
          }
        },
      );
      soundRef.current = sound;
      setPlaying(true);
    } catch {
      // audio 로드 실패는 무시
    } finally {
      setLoading(false);
    }
  };

  const label = loading ? '로딩 중...' : playing ? '일시 정지' : '재생';
  const icon = loading ? '⏳' : playing ? '⏸' : '▶';

  return (
    <TouchableOpacity
      style={[styles.button, loading && styles.buttonDisabled]}
      onPress={togglePlay}
      disabled={loading}
    >
      <Text style={styles.icon}>{icon}</Text>
      <Text style={styles.label}>{label}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    backgroundColor: '#03dac6',
    borderRadius: 12,
    padding: 16,
  },
  buttonDisabled: { opacity: 0.6 },
  icon: { fontSize: 20 },
  label: { fontSize: 16, fontWeight: '600', color: '#fff' },
});
