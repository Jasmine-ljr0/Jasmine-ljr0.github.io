// OrbitalType — 复刻 React Bits「Orbital Type」观感的自包含动效背景：
// 文字沿球体纬线环抱、前后景双色、整体低透明度，突出上层人物主体。
// 纯 React + CSS，无第三方依赖，与项目配色体系（--olive / --tan）联动。

export default function OrbitalType({
  text = '文案 · 策划 · 品牌 · 内容营销 · 新媒体 · ',
  frontColor = 'var(--olive)',
  backColor = 'var(--tan)',
  bands = 15,
  className = '',
}) {
  const rings = Array.from({ length: bands }, (_, i) => {
    const t = bands === 1 ? 0.5 : i / (bands - 1) // 0（顶）→ 1（底）
    const lat = (t - 0.5) * Math.PI // -π/2 → π/2
    const cos = Math.cos(lat) // 赤道=1，两极=0（环宽）
    const sin = Math.sin(lat) // 深度与上下位置
    const top = 50 + sin * 50 // %
    const width = Math.max(6, cos * 100) // %
    const isBack = sin < 0 // 远侧（上半）更暗
    const dir = i % 2 === 0 ? 'normal' : 'reverse' // 相邻环反向流动
    const dur = (7 + cos * 11).toFixed(2) // 赤道环更慢，两极更快
    const depth = (sin * 16).toFixed(2) // 轻微 3D 进深（px，按比例）
    return { top, width, isBack, dir, dur, depth, key: i }
  })

  return (
    <div className={`orbital ${className}`} aria-hidden="true">
      <div className="orbital-globe">
        {rings.map((r) => (
          <div
            key={r.key}
            className="orbital-ring"
            style={{
              top: `${r.top}%`,
              width: `${r.width}%`,
              opacity: r.isBack ? 0.4 : 1,
              color: r.isBack ? backColor : frontColor,
              transform: `translate(-50%, -50%) translateZ(${r.depth}px)`,
            }}
          >
            <div
              className="orbital-track"
              style={{ animationDuration: `${r.dur}s`, animationDirection: r.dir }}
            >
              <span>{text.repeat(3)}</span>
              <span>{text.repeat(3)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
