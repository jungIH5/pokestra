import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';

export default function RootLayout() {
  return (
    <>
      <StatusBar style="dark" />
      <Stack screenOptions={{ headerTintColor: '#6200ee' }}>
        <Stack.Screen name="index" options={{ title: 'Photo Maestro' }} />
        <Stack.Screen name="result/[jobId]" options={{ title: '분석 결과' }} />
        <Stack.Screen name="history" options={{ title: '히스토리' }} />
      </Stack>
    </>
  );
}
