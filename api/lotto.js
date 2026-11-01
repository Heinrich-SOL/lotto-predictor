/**
 * Vercel Serverless Function: 동행복권 공식 당첨번호 조회 프록시 API
 * 브라우저 CORS 제한 없이 실시간 당첨번호를 JSON으로 반환합니다.
 */

export default async function handler(req, res) {
  // CORS 헤더 허용
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');
  res.setHeader('Cache-Control', 's-maxage=3600, stale-while-revalidate=86400');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const { drwNo } = req.query;

  if (!drwNo) {
    return res.status(400).json({ error: 'drwNo parameter is required (e.g. ?drwNo=1248)' });
  }

  try {
    const targetUrl = `https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo=${drwNo}`;
    const response = await fetch(targetUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });

    if (!response.ok) {
      return res.status(response.status).json({ error: `동행복권 서버 응답 오류 (${response.status})` });
    }

    const data = await response.json();
    return res.status(200).json(data);
  } catch (err) {
    return res.status(500).json({ error: '당첨번호 조회 실패', message: err.message });
  }
}
