/**
 * Vercel Serverless Function: 동행복권 공식 당첨번호 조회 프록시 API
 * 브라우저 CORS 제한 없이 실시간 당첨번호를 JSON으로 반환합니다.
 * (신규 공식 API 대응 및 구형 필드 규격 호환 변환)
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
    return res.status(400).json({ error: 'drwNo parameter is required (e.g. ?drwNo=1249)' });
  }

  const headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
  };

  // 1. 신규 엔드포인트 시도
  try {
    const newUrl = `https://www.dhlottery.co.kr/lt645/selectPstLt645Info.do?srchLtEpsd=${drwNo}`;
    const response = await fetch(newUrl, { headers });
    if (response.ok) {
      const json = await response.json();
      const list = json?.data?.list;
      if (list && list.length > 0) {
        const item = list[0];
        const dateRaw = String(item.ltRflYmd || '');
        const dateStr = dateRaw.length === 8 ? `${dateRaw.slice(0, 4)}-${dateRaw.slice(4, 6)}-${dateRaw.slice(6)}` : dateRaw;

        return res.status(200).json({
          returnValue: 'success',
          drwNo: item.ltEpsd,
          drwNoDate: dateStr,
          drwtNo1: item.tm1WnNo,
          drwtNo2: item.tm2WnNo,
          drwtNo3: item.tm3WnNo,
          drwtNo4: item.tm4WnNo,
          drwtNo5: item.tm5WnNo,
          drwtNo6: item.tm6WnNo,
          bnusNo: item.bnsWnNo,
          firstWinamnt: item.rnk1WnAmt || 0,
          firstPrzwnerCo: item.rnk1WnNope || 0
        });
      }
    }
  } catch (err) {
    // 신규 API 실패 시 구형 API 시도
  }

  // 2. 구형 엔드포인트 폴백
  try {
    const oldUrl = `https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo=${drwNo}`;
    const response = await fetch(oldUrl, { headers });
    if (response.ok) {
      const data = await response.json();
      return res.status(200).json(data);
    }
  } catch (err) {
    return res.status(500).json({ error: '당첨번호 조회 실패', message: err.message });
  }

  return res.status(404).json({ error: `제${drwNo}회 당첨결과를 찾을 수 없습니다.` });
}
