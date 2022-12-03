import math
from dataclasses import dataclass


class Range:
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop

    @property
    def width(self):
        assert self.start <= self.stop
        return self.stop - self.start

    def __add__(self, other: int):
        return Range(self.stop, self.stop + other)

    def __iter__(self):
        return iter([self.start, self.stop])


@dataclass
class GlobalParameters:
    ''' 가시화를 위한 영역 범위 '''
    # 드론이 모니터링하는 영역의 x축 범위 (기본: 0 이상 100 미만)
    DroneXRange: Range = Range(0, 100)
    # 에지 서버 배치 영역의 x축 범위 (기본: 100 이상 140 미만)
    EdgeServerXRange: Range = DroneXRange + 40
    # 클라우드 서버 배치 영역의 x축 범위 (기본: 140 이상 200 미만)
    CloudServerXRange: Range = EdgeServerXRange + 60
    # 전체 영역 너비, 높이
    AreaXRange: Range = Range(DroneXRange.start, CloudServerXRange.stop)
    AreaYRange: Range = Range(0, 100)
    EdgeServerYRange: Range = Range(0, 100)
    CloudServerYRange: Range = Range(0, 100)

    ''' 통신 반경 파라미터 '''
    DroneTransRange: float = 30  # 드론의 통신 반경 (기본: 100)
    EdgeServerTransRange: float = math.inf
    CloudServerTransRange: float = math.inf


    ''' 네트워크 토폴리지의 드론, 에지 서버, 클라우드 서버의 수 '''
    NumOfDrones: int = 30  # UAV의 수 (기본: 30),
    NumOfEdgeServer: int = 4  # 에지 서버의 수 (기본: 4)
    NumOfCloudServer: int = 2  # 클라우드 서버의 수 (기본: 2)

    ''' 프로세싱 Rate 파라미터 '''
    MaxProcessingRateOfDrone: int = 100  # 드론의 프로세싱 rate 파라미터 (기본: 100)
    MaxProcessingRateOfEdgeServer: int = 500  # 에지 서버의 프로세싱 rate 파라미터 (기본: 500)
    MaxProcessingRateOfCloudServer: int = 10000  # 클라우드 서버의 프로세싱 rate 파라미터 (기본: 10000)

    ''' 딜레이 Factor 파라미터 '''
    MaxDelayFactorOfDrone: int = 1  # 드론의 딜레이 factor (기본: 1)
    MaxDelayFactorOfEdgeServer: int = 5  # 에지 서버의 딜레이 factor (기본: 5)
    MaxDelayFactorOfCloudServer: int = 6   # 클라우드 서버의 딜레이 factor (기본: 6)

    ''' 대역폭 파라미터 '''
    BandwidthOfDrone: int = 200  # 드론의 대역폭 (기본: 200)
    BandwidthOfEdgeServer: int = 400  # 에지 서버의 대역폭 (기본: 400)
    BandwidthOfCloudServer: int = 1000  # 클라우드 서버의 대역폭 (기본: 1000)

    ''' 워크플로우 관련 파라미터 '''
    NumOfWorkflows: int = 20  # 워크플로우 수 (기본: 4)
    MinTasksPerWorkFlow: int = 4  # 하나의 워크플로우의 최소 태스크 수 (기본: 4)
    MaxTasksPerWorkflow: int = 4  # 하나의 워크플로우의 최대 태스크 수 (기본: 4)
    MinRequiredProcessingPower: int = 20  # 각 태스크의 최소 소모 프로세싱 파워 (기본: 50)
    MaxRequiredProcessingPower: int = 30  # 각 태스크의 최대 소모 프로세싱 파워 (기본: 1000)
    MinRequiredBandwidth: int = 20  # 각 태스크의 최소 대역폭 파워 (기본: 50)
    MaxRequiredBandwidth: int = 30  # 각 태스크의 최대 대역폭 파워 (기본: 200)


Xlarge_test_parameters = GlobalParameters(
    DroneXRange = Range(0, 160),
    EdgeServerXRange = Range(160, 180),
    CloudServerXRange = Range(180, 200),
    AreaXRange = Range(0, 200),
    AreaYRange = Range(0, 200),
    EdgeServerYRange = Range(0, 200),
    CloudServerYRange = Range(0, 200),

    DroneTransRange = 50,
    EdgeServerTransRange = math.inf,
    CloudServerTransRange = math.inf,

    NumOfDrones = 100,
    NumOfEdgeServer = 10,
    NumOfCloudServer = 4,

    MaxProcessingRateOfDrone = 100,
    MaxProcessingRateOfEdgeServer = 500,
    MaxProcessingRateOfCloudServer = 10000,

    MaxDelayFactorOfDrone = 1,
    MaxDelayFactorOfEdgeServer = 5,
    MaxDelayFactorOfCloudServer = 6,

    BandwidthOfDrone = 200,
    BandwidthOfEdgeServer = 400,
    BandwidthOfCloudServer = 1000,

    NumOfWorkflows = 30,
    MinTasksPerWorkFlow = 4,
    MaxTasksPerWorkflow = 8,
    MinRequiredProcessingPower = 40,
    MaxRequiredProcessingPower = 80,
    MinRequiredBandwidth = 20,
    MaxRequiredBandwidth = 30
)


vanilla_test_parameters = GlobalParameters(
    DroneXRange = Range(0, 30),
    EdgeServerXRange = Range(30, 40),
    CloudServerXRange = Range(40, 50),
    AreaXRange = Range(0, 50),
    AreaYRange = Range(0, 30),
    EdgeServerYRange = Range(0, 30),
    CloudServerYRange = Range(0, 30),

    DroneTransRange = 10,
    EdgeServerTransRange = math.inf,
    CloudServerTransRange = math.inf,

    NumOfDrones = 10,
    NumOfEdgeServer = 4,
    NumOfCloudServer = 2,

    MaxProcessingRateOfDrone = 100,
    MaxProcessingRateOfEdgeServer = 500,
    MaxProcessingRateOfCloudServer = 10000,

    MaxDelayFactorOfDrone = 1,
    MaxDelayFactorOfEdgeServer = 5,
    MaxDelayFactorOfCloudServer = 6,

    BandwidthOfDrone = 200,
    BandwidthOfEdgeServer = 400,
    BandwidthOfCloudServer = 1000,

    NumOfWorkflows = 4,
    MinTasksPerWorkFlow = 4,
    MaxTasksPerWorkflow = 4,
    MinRequiredProcessingPower = 40,
    MaxRequiredProcessingPower = 80,
    MinRequiredBandwidth = 20,
    MaxRequiredBandwidth = 30
)

super_vanilla_test_parameters = GlobalParameters(
    DroneXRange = Range(0, 10),
    EdgeServerXRange = Range(10, 15),
    CloudServerXRange = Range(15, 20),
    AreaXRange = Range(0, 20),
    AreaYRange = Range(0, 20),
    EdgeServerYRange = Range(0, 20),
    CloudServerYRange = Range(0, 20),

    DroneTransRange = 5,
    EdgeServerTransRange = math.inf,
    CloudServerTransRange = math.inf,

    NumOfDrones = 4,
    NumOfEdgeServer = 2,
    NumOfCloudServer = 1,

    MaxProcessingRateOfDrone = 100,
    MaxProcessingRateOfEdgeServer = 500,
    MaxProcessingRateOfCloudServer = 10000,

    MaxDelayFactorOfDrone = 1,
    MaxDelayFactorOfEdgeServer = 5,
    MaxDelayFactorOfCloudServer = 6,

    BandwidthOfDrone = 200,
    BandwidthOfEdgeServer = 400,
    BandwidthOfCloudServer = 1000,

    NumOfWorkflows = 2,
    MinTasksPerWorkFlow = 4,
    MaxTasksPerWorkflow = 4,
    MinRequiredProcessingPower = 40,
    MaxRequiredProcessingPower = 80,
    MinRequiredBandwidth = 20,
    MaxRequiredBandwidth = 30
)

DEBUG = False
DEBUG_ALL_CASES = False


global_params = Xlarge_test_parameters
#global_params = GlobalParameters()  # large
#global_params = vanilla_test_parameters  # small
#global_params = super_vanilla_test_parameters
