export { Surface } from "@/design/primitives/Surface";
export { Text } from "@/design/primitives/Text";
export { Button } from "@/design/primitives/Button";
export { Input } from "@/design/primitives/Input";
export { Badge, Chip } from "@/design/primitives/Badge";
export { Icon } from "@/design/primitives/Icon";

export { PageEnter } from "@/design/motion/PageEnter";
export { NumberTick } from "@/design/motion/NumberTick";
export { StateCrossfade } from "@/design/motion/StateCrossfade";

export { AppShell } from "@/design/shells/AppShell";
export { PageHeader } from "@/design/shells/PageHeader";
export { ActionRail } from "@/design/shells/ActionRail";
export { ThemeSwitcher } from "@/design/shells/ThemeSwitcher";
export { DeskFooter } from "@/design/shells/DeskFooter";
export { MobileTopBar } from "@/design/shells/MobileTopBar";
export { MobileBottomNav } from "@/design/shells/MobileBottomNav";
export { APP_NAV_LINKS, linkActive } from "@/design/shells/nav-config";

export { MetricStrip } from "@/design/patterns/MetricStrip";
export { EmptyState } from "@/design/patterns/EmptyState";
export { Skeleton, SkeletonText, SkeletonMetric } from "@/design/patterns/Skeleton";
export { SectionWrap } from "@/design/patterns/SectionWrap";
export { HOME_COPY } from "@/design/patterns/home-copy";
export { ASSET_COPY } from "@/design/patterns/asset-copy";
export { AssetSection } from "@/design/patterns/AssetSection";
export {
  MarketPulse,
  PulseMetric,
  PulseHonesty,
  PulseLiveMark,
  PulseAtmosphere,
  PulseHero,
  PulseSpectrum,
  mixFromRegimes,
  type MarketPulseProps,
  type PulseFocus,
  type PulseRegimeMix,
} from "@/design/patterns/market-pulse";

export {
  DeskHero,
  DeskHeroAtmosphere,
  HeroFeaturedPrice,
  HeroPressLane,
  HeroSparkStrip,
  HeroTape,
  DESK_HERO_STAGES,
  DESK_HERO_DEFAULT,
  type DeskHeroProps,
  type DeskHeroStageId,
} from "@/design/patterns/desk-hero";

export {
  Universe,
  UniverseAtmosphere,
  UniverseFilter,
  UniverseTimeframe,
  UniverseInstrument,
  UniverseMiniChart,
  UniverseVolGauge,
  UniverseVolBar,
  UniverseSentiment,
  UNIVERSE_SPARK_DEFAULT,
  UNIVERSE_SPARK_TIMEFRAMES,
  UNIVERSE_SPARK_LABEL,
  type UniverseProps,
  type UniverseFilterKey,
  type UniverseSparkTimeframe,
} from "@/design/patterns/universe";

export {
  SignalTicker,
  TickerAtmosphere,
  TickerFocus,
  TickerLead,
  TickerFilter,
  TickerHeadline,
  TickerImpact,
  TickerMast,
  TickerPressure,
  TickerStream,
  normalizeImpact,
  impactLabel,
  impactToneVar,
  countByImpact,
  type SignalTickerProps,
  type TickerFilterKey,
  type ImpactLevel,
} from "@/design/patterns/news-ticker";

export {
  ChartFrame,
  useChartTheme,
  readChartTheme,
  colorForTone,
  cssVarStroke,
  DS_CHART_TYPES,
  DS_CHART_DEFAULT,
  DS_CHART_LABEL,
  type ChartTheme,
  type DsChartType,
} from "@/design/patterns/charts";

export {
  PriceRegimeChart,
  PriceTimeframe,
  PriceChartType,
  ASSET_BAR_DEFAULT,
  ASSET_BAR_TIMEFRAMES,
  ASSET_BAR_LABEL,
  type PriceRegimeChartProps,
  type AssetBarTimeframe,
} from "@/design/patterns/price-regime";

export {
  SentimentScale,
  SentimentField,
  SentimentAtmosphere,
  SentimentMast,
  SentimentDial,
  SentimentSpectrum,
  SentimentDriverPeek,
  SentimentFocus,
} from "@/design/patterns/sentiment";
export {
  DriverPress,
  DriverPressAtmosphere,
  DriverPressMast,
  DriverPressLead,
  DriverPressStream,
} from "@/design/patterns/driver-press";
export {
  InsightBrief,
  InsightAtmosphere,
  InsightMast,
  InsightBody,
  InsightTagRail,
  InsightRefs,
  InsightFocus,
} from "@/design/patterns/insight-brief";
export { RegimeProbabilityBars, RegimeDistributionBars, RegimeHistoryField, RegimeNowcastField } from "@/design/patterns/state";
export {
  RegimeHistoryAtmosphere,
  RegimeHistoryMast,
  RegimeHistoryDial,
  RegimeHistoryStack,
  RegimeHistoryLanes,
  RegimeHistoryFocus,
} from "@/design/patterns/regime-history";
export {
  RegimeNowcastAtmosphere,
  RegimeNowcastMast,
  RegimeNowcastDial,
  RegimeNowcastStack,
  RegimeNowcastMetrics,
  RegimeNowcastFocus,
} from "@/design/patterns/regime-nowcast";
export { CorrelationField, CorrelationMatrix } from "@/design/patterns/correlation";
export { EventSensitivityList, ProfileDossier, EventSensitivityField } from "@/design/patterns/profile";
export {
  EventSensitivityAtmosphere,
  EventSensitivityMast,
  EventSensitivityDial,
  EventSensitivityRail,
  EventSensitivityFocus,
} from "@/design/patterns/event-sensitivity";
export { FitTagChip, FitField, FitOverlay, FitHeroChip } from "@/design/patterns/fit";
export { ScoringAccuracyTrend, ScoringSymbolBars } from "@/design/patterns/scoring";
export { PipeLagChart, OutboxMix } from "@/design/patterns/desk";
export { NewsImpactBars } from "@/design/patterns/news";
export {
  DeskStage,
  DeskSignalField,
  LoadingDesk,
  LostDesk,
} from "@/design/patterns/desk-stage";

export {
  toneForRegime,
  toneForStale,
  toneForFeedStatus,
  toneForZone,
  toneForLifecycle,
  toneForGate,
  toneForFitTag,
  cssVarForTone,
  REGIME_LABEL,
  type SemanticTone,
  type Regime,
} from "@/design/map/backend-visual";
