.PHONY: run dev test help

help:
	@echo "ChronoMine AI / SwissTunnelCopilot — Hack Apertus Track 2B"
	@echo "Commands:"
	@echo "  make run  - Start the project in Docker container (Hackathon requirement)"
	@echo "  make dev  - Start local backend development server"
	@echo "  make test - Run test suite"

run:
	$(MAKE) -C track_2b run

dev:
	$(MAKE) -C track_2b dev

test:
	$(MAKE) -C track_2b test
