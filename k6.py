import http from 'k6/http';
import { sleep, check } from 'k6';

// --------------------------------------------------
// 설정
// --------------------------------------------------

const BASE_URL = 'https://d33nd37o8cwhu4.cloudfront.net';

// 전체 콘텐츠 ID 후보 (1~10번)
const ALL_CONTENT_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

// --------------------------------------------------
// 실행 시작 시 한 번만: 이번 실행에서 "화제작"이 될 콘텐츠를 랜덤으로 뽑는다
// (setup 함수는 k6 실행 시작할 때 딱 한 번만 실행됨)
// --------------------------------------------------

export function setup() {
  // 화제작 개수도 1~2개 사이에서 랜덤
  const hotCount = Math.random() < 0.5 ? 1 : 2;

  // 후보 목록을 섞어서 앞에서부터 hotCount개를 화제작으로 선정
  const shuffled = [...ALL_CONTENT_IDS].sort(() => Math.random() - 0.5);
  const hotContentIds = shuffled.slice(0, hotCount);
  const normalContentIds = shuffled.slice(hotCount);

  console.log(`==================================================`);
  console.log(`🔥 [신작 오픈] 이번 실행의 화제작: ${JSON.stringify(hotContentIds)}`);
  console.log(`🎬 [평범한 콘텐츠들]: ${JSON.stringify(normalContentIds)}`);
  console.log(`==================================================`);

  return { hotContentIds, normalContentIds };
}

// --------------------------------------------------
// 실행 옵션: VU 수도 매번 실행할 때 살짝 랜덤하게
// (options는 스크립트 로드 시점에 정해지므로, 범위를 두고 코드에서 활용)
// --------------------------------------------------

export const options = {
  scenarios: {
    hot_content_surge: {
      executor: 'constant-vus',
      vus: 20 + Math.floor(Math.random() * 10), // 20~29명 집중 유입
      duration: '1m', // 10분 발표에 맞게 1분 집중 실행
      exec: 'hitHotContent',
    },
    background_traffic: {
      executor: 'constant-vus',
      vus: 2 + Math.floor(Math.random() * 3), // 2~4명 분산 유입
      duration: '1m', // 10분 발표에 맞게 1분 집중 실행
      exec: 'hitNormalContent',
    },
  },
};

// --------------------------------------------------
// 1. 화제작 집중 요청 (setup에서 뽑힌 콘텐츠 중 랜덤으로 하나씩)
// --------------------------------------------------

export function hitHotContent(data) {
  const ids = data.hotContentIds;
  const id = ids[Math.floor(Math.random() * ids.length)];

  // 💡 가상 유저별 분산 IP 생성 (211.234.1.x ~ 211.234.30.x)
  const virtualIp = `211.234.${__VU}.${(__ITER % 250) + 1}`;

  // 💡 터미널 실시간 출력
  console.log(`[🔥 화제작 VU ${__VU}] IP: ${virtualIp} ➔ /api/contents/${id}`);

  const params = {
    headers: {
      'X-Client-IP': virtualIp,
      'X-User-IP': virtualIp,
      'X-Forwarded-For': virtualIp,
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    },
  };

  // 💡 URL 쿼리 파라미터로 가상 IP 전송 (CloudWatch 로그 완벽 연동)
  const targetUrl = `${BASE_URL}/api/contents/${id}?client_ip=${virtualIp}`;
  const res = http.get(targetUrl, params);

  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  // 요청 간격: 0.1~0.5초 사이 랜덤 (빠른 연속 시청 유입)
  sleep(0.1 + Math.random() * 0.4);
}

// --------------------------------------------------
// 2. 평범한 콘텐츠 요청 (배경 트래픽)
// --------------------------------------------------

export function hitNormalContent(data) {
  const ids = data.normalContentIds;
  if (ids.length === 0) {
    sleep(1);
    return;
  }
  const id = ids[Math.floor(Math.random() * ids.length)];

  // 💡 배경 트래픽용 분산 IP 생성 (211.234.101.x ~)
  const virtualIp = `211.234.${__VU + 100}.${(__ITER % 250) + 1}`;

  // 💡 터미널 실시간 출력
  console.log(`[🎬 일반작 VU ${__VU}] IP: ${virtualIp} ➔ /api/contents/${id}`);

  const params = {
    headers: {
      'X-Client-IP': virtualIp,
      'X-User-IP': virtualIp,
      'X-Forwarded-For': virtualIp,
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    },
  };

  // 💡 URL 쿼리 파라미터로 가상 IP 전송 (CloudWatch 로그 완벽 연동)
  const targetUrl = `${BASE_URL}/api/contents/${id}?client_ip=${virtualIp}`;
  const res = http.get(targetUrl, params);

  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  // 배경 트래픽은 좀 더 느긋하게: 1~3초 사이 랜덤
  sleep(1 + Math.random() * 2);
}
