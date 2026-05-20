import { useState } from 'react';
import { Image, View, Text, StyleSheet, ActivityIndicator } from 'react-native';

interface Props {
  url: string;
}

export function SheetMusicView({ url }: Props) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  if (error) {
    return (
      <View style={styles.placeholder}>
        <Text style={styles.placeholderText}>악보를 불러올 수 없습니다</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {loading && (
        <ActivityIndicator style={StyleSheet.absoluteFill} color="#6200ee" />
      )}
      <Image
        source={{ uri: url }}
        style={styles.image}
        resizeMode="contain"
        onLoadEnd={() => setLoading(false)}
        onError={() => {
          setLoading(false);
          setError(true);
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: '100%',
    minHeight: 200,
    backgroundColor: '#fafafa',
    borderRadius: 12,
    overflow: 'hidden',
  },
  image: { width: '100%', height: 260 },
  placeholder: {
    height: 200,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
  },
  placeholderText: { color: '#999', fontSize: 14 },
});
