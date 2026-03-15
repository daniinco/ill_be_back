import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  scenarios: {
    ramp: {
      executor: 'ramping-arrival-rate',
      startRate: 1,
      timeUnit: '1s',
      preAllocatedVUs: 50,
      maxVUs: 200,
      stages: [
        { target: 10, duration: '30s' },
        { target: 30, duration: '30s' },
        { target: 50, duration: '30s' },
        { target: 0, duration: '10s' },
      ],
    },
  },
};

const BASE = __ENV.BASE_URL || 'http://localhost:8003';

let userCounter = 1;
let adCounter = 1;

export default function () {
  const headers = { 'Content-Type': 'application/json' };

  const userPayload = JSON.stringify({
    name: `TestUser_${userCounter++}`,
    is_verified: Math.random() > 0.5
  });

  const userResponse = http.post(`${BASE}/users`, userPayload, { headers });
  check(userResponse, {
    'user created': (r) => r.status === 200,
  });

  let userId = 1;
  if (userResponse.status === 200) {
    try {
      userId = JSON.parse(userResponse.body).id;
    } catch (e) {}
  }

  const adPayload = JSON.stringify({
    user_id: userId,
    item_id: adCounter++,
    name: 'Test Product',
    description: 'Test description for load testing',
    category: Math.floor(Math.random() * 10) + 1,
    images_qty: Math.floor(Math.random() * 5) + 1
  });

  const adResponse = http.post(`${BASE}/advertisements`, adPayload, { headers });
  check(adResponse, {
    'ad created': (r) => r.status === 200,
  });

  let adId = 1;
  if (adResponse.status === 200) {
    try {
      adId = JSON.parse(adResponse.body).id;
    } catch (e) {}
  }

  const predictPayload = JSON.stringify({
    seller_id: userId,
    is_verified_seller: Math.random() > 0.5,
    item_id: adId,
    name: 'Test Product',
    description: 'Test description',
    category: 5,
    images_qty: 3
  });

  const responses = [
    http.post(`${BASE}/predict`, predictPayload, { headers }),
    http.post(`${BASE}/simple_predict?item_id=${adId}`, null, { headers }),
    http.get(`${BASE}/`),
  ];

  responses.forEach(res => {
    check(res, {
      'status is 200 or 404': (r) => r.status === 200 || r.status === 404,
    });
  });

  sleep(0.1);
}