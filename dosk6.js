import http from 'k6/http';
import { check } from 'k6';

// --------------------------------------------------
// AIOps 장애 대응 검증용: 비정상 고부하/DoS 시뮬레이션 스크립트
// --------------------------------------------------

const BASE_URL = 'https://d33nd37o8cwhu4.cloudfront.net';

// 💡 단일 공격자 고정 IP 시뮬레이션 (CloudWatch 로그에서 단일 IP 집중도로 식별됨)
const ATTACKER_IP = '198.51.100.23';

export const options = {
  vus: 8,           // 8명의 가상 봇이 고비용 연산을 초집중 호출
  duration: '1m',   // 10분 발표에 맞춰 1분간 초고밀도 부하 주입
};

export default function () {
  // 💥 고비용 CPU 부하 엔드포인트를 집중 호출하여 즉각적인 CPU 스파이크 및 이상 탐지 유발
  const targetUrl = `${BASE_URL}/api/ops/cpu-load?duration=5&client_ip=${ATTACKER_IP}`;

  const params = {
    headers: {
      'User-Agent': 'AnomalousTrafficBot/1.0',
      'X-Client-IP': ATTACKER_IP,
      'X-User-IP': ATTACKER_IP,
      'X-Forwarded-For': ATTACKER_IP,
    },
    timeout: '15s',
  };

  // 💡 터미널 실시간 출력
  console.log(`[💥 DoS 부하 VU ${__VU}] 발송 IP: ${ATTACKER_IP} ➔ /api/ops/cpu-load`);

  const res = http.post(targetUrl, null, params);

  check(res, {
    'status is 200 or 504': (r) => r.status === 200 || r.status === 504 || r.status === 500,
  });

  // 💡 딜레이(sleep) 없이 지속적으로 연타하여 단일 IP 비정상 편중도 극대화
}
