import { View, Text, FlatList, TouchableOpacity, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { useJobStore, HistoryEntry } from '../store/jobStore';

export default function HistoryScreen() {
  const router = useRouter();
  const { history } = useJobStore();

  if (history.length === 0) {
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyText}>아직 생성된 음악이 없습니다</Text>
        <TouchableOpacity style={styles.goButton} onPress={() => router.back()}>
          <Text style={styles.goButtonText}>첫 번째 음악 만들기</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const renderItem = ({ item }: { item: HistoryEntry }) => (
    <TouchableOpacity
      style={styles.card}
      onPress={() => router.push(`/result/${item.job_id}`)}
    >
      <View>
        <Text style={styles.cardType}>
          {item.result.image_type === 'sheet_music' ? '악보 인식' : '이미지 분석'}
        </Text>
        {item.result.music_params && (
          <Text style={styles.cardSub}>
            {String(item.result.music_params.scale ?? '')} ·{' '}
            {String(item.result.music_params.mood ?? '')}
          </Text>
        )}
      </View>
      <Text style={styles.cardDate}>
        {new Date(item.timestamp).toLocaleString('ko-KR', {
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        })}
      </Text>
    </TouchableOpacity>
  );

  return (
    <FlatList
      data={history}
      keyExtractor={(item) => item.job_id}
      renderItem={renderItem}
      contentContainerStyle={styles.list}
      style={styles.container}
    />
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  list: { padding: 16, gap: 10 },
  card: {
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  cardType: { fontSize: 15, fontWeight: '600', color: '#333' },
  cardSub: { fontSize: 13, color: '#777', marginTop: 2 },
  cardDate: { fontSize: 12, color: '#aaa' },
  empty: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 20,
    backgroundColor: '#fff',
  },
  emptyText: { fontSize: 16, color: '#999' },
  goButton: {
    backgroundColor: '#6200ee',
    borderRadius: 14,
    paddingHorizontal: 28,
    paddingVertical: 14,
  },
  goButtonText: { color: '#fff', fontSize: 15, fontWeight: '600' },
});
