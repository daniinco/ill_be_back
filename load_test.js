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

export default function () {
  const validPayload = JSON.stringify({
    seller_id: 1,
    is_verified_seller: true,
    item_id: 100,
    name: 'Test',
    description: '',
    category: 5,
    images_qty: 3
  });

  const invalidPayload = JSON.stringify({
    seller_id: 1,
    is_verified_seller: false,
    item_id: 200,
    name: 'Bad Product',
    description: '',
    category: 99,
    images_qty: 0
  });

  const headers = { 'Content-Type': 'application/json' };

  const responses = [
    http.post(`${BASE}/predict`, validPayload, { headers }),
    http.post(`${BASE}/predict`, invalidPayload, { headers }),
    http.post(`${BASE}/simple_predict?item_id=1`, null, { headers }),
    http.get(`${BASE}/`),
  ];

  responses.forEach(res => {
    check(res, {
      'status is 200 or 404': (r) => r.status === 200 || r.status === 404,
    });
  });

  sleep(0.1);
}