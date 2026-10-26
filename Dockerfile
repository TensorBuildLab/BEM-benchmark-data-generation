# bemgen + EnergyPlus 23.1 in one image.
#   docker build -t bemgen .
#   docker run --rm -v "$PWD:/work" -w /work bemgen bemgen qa benchmark/items/S3/V02-small-office-chicago --weather work/weather
FROM nrel/energyplus:23.1.0 AS eplus

FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 libx11-6 && rm -rf /var/lib/apt/lists/*
COPY --from=eplus /EnergyPlus-23.1.0-87ed9199d4-Linux-Ubuntu20.04-x86_64 /opt/EnergyPlus-23.1.0
ENV BEMGEN_ENERGYPLUS=/opt/EnergyPlus-23.1.0/energyplus \
    BEMGEN_SCHEMA=/opt/EnergyPlus-23.1.0/Energy+.schema.epJSON \
    PATH=/opt/EnergyPlus-23.1.0:$PATH
WORKDIR /opt/bemgen
COPY pyproject.toml README.md LICENSE.txt ./
COPY src ./src
RUN pip install --no-cache-dir ".[ingest,test]"
WORKDIR /work
CMD ["bemgen", "--help"]
