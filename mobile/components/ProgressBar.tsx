import { View, StyleSheet } from 'react-native';

interface Props {
  progress: number;
}

export function ProgressBar({ progress }: Props) {
  const clamped = Math.min(100, Math.max(0, progress));
  return (
    <View style={styles.track}>
      <View style={[styles.fill, { width: `${clamped}%` }]} />
    </View>
  );
}

const styles = StyleSheet.create({
  track: {
    width: '100%',
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
    overflow: 'hidden',
  },
  fill: {
    height: '100%',
    backgroundColor: '#6200ee',
    borderRadius: 4,
  },
});
