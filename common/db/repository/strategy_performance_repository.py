from common.db.repository.base_repository import BaseRepository
from common.db.models.strategy_performance import StrategyPerformance
from typing import Optional, List


class StrategyPerformanceRepository(BaseRepository):
    """Repository for StrategyPerformance model"""

    def __init__(self, session):
        super().__init__(session, StrategyPerformance)

    def get_by_user_and_strategy(self, user_id: int, strategy_name: str) -> Optional[StrategyPerformance]:
        """Get performance metrics for user and strategy

        Args:
            user_id: User ID
            strategy_name: Strategy name

        Returns:
            StrategyPerformance or None
        """
        return self.session.query(StrategyPerformance).filter(
            StrategyPerformance.user_id == user_id,
            StrategyPerformance.strategy_name == strategy_name
        ).first()

    def get_user_strategies(self, user_id: int) -> List[StrategyPerformance]:
        """Get all strategy performance metrics for user

        Args:
            user_id: User ID

        Returns:
            List of StrategyPerformance
        """
        return self.session.query(StrategyPerformance).filter(
            StrategyPerformance.user_id == user_id
        ).order_by(StrategyPerformance.win_rate.desc()).all()

    def get_top_strategies(self, limit: int = 10) -> List[StrategyPerformance]:
        """Get top performing strategies across all users

        Args:
            limit: Number of strategies to return

        Returns:
            List of StrategyPerformance
        """
        return self.session.query(StrategyPerformance).order_by(
            StrategyPerformance.win_rate.desc()
        ).limit(limit).all()

    def update_metrics(
        self,
        user_id: int,
        strategy_name: str,
        total_trades: int,
        winning_trades: int,
        losing_trades: int,
        total_pnl: float,
        avg_profit: float,
        avg_loss: float,
        max_profit: float,
        max_loss: float,
        max_drawdown: float,
        profit_factor: float,
        sharpe_ratio: float,
        sortino_ratio: float,
        total_signals: int,
        executed_signals: int
    ) -> bool:
        """Update strategy performance metrics

        Args:
            user_id: User ID
            strategy_name: Strategy name
            total_trades: Total number of trades
            winning_trades: Number of winning trades
            losing_trades: Number of losing trades
            total_pnl: Total profit/loss
            avg_profit: Average profit per winning trade
            avg_loss: Average loss per losing trade
            max_profit: Maximum profit
            max_loss: Maximum loss
            max_drawdown: Maximum drawdown
            profit_factor: Gross profit / Gross loss
            sharpe_ratio: Sharpe ratio
            sortino_ratio: Sortino ratio
            total_signals: Total signals generated
            executed_signals: Signals that were executed

        Returns:
            True if successful
        """
        try:
            perf = self.get_by_user_and_strategy(user_id, strategy_name)

            if not perf:
                perf = StrategyPerformance(
                    user_id=user_id,
                    strategy_name=strategy_name
                )
                self.session.add(perf)

            perf.total_trades = total_trades
            perf.winning_trades = winning_trades
            perf.losing_trades = losing_trades
            perf.win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
            perf.total_pnl = total_pnl
            perf.avg_profit = avg_profit
            perf.avg_loss = avg_loss
            perf.max_profit = max_profit
            perf.max_loss = max_loss
            perf.max_drawdown = max_drawdown
            perf.profit_factor = profit_factor
            perf.sharpe_ratio = sharpe_ratio
            perf.sortino_ratio = sortino_ratio
            perf.total_signals = total_signals
            perf.executed_signals = executed_signals
            perf.signal_accuracy = executed_signals / total_signals if total_signals > 0 else 0.0

            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            raise e

    def get_aggregate_stats(self, user_id: int) -> dict:
        """Get aggregate statistics for all strategies

        Args:
            user_id: User ID

        Returns:
            Dictionary with aggregate stats
        """
        from sqlalchemy import func

        strategies = self.get_user_strategies(user_id)
        total_trades = sum(s.total_trades for s in strategies)
        total_pnl = sum(s.total_pnl for s in strategies)
        avg_win_rate = sum(s.win_rate for s in strategies) / len(strategies) if strategies else 0.0

        return {
            "strategy_count": len(strategies),
            "total_trades": total_trades,
            "total_pnl": total_pnl,
            "avg_win_rate": avg_win_rate,
            "best_strategy": max(strategies, key=lambda x: x.win_rate).strategy_name if strategies else None,
        }
