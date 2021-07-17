from typing import NamedTuple
import math


DEBUG = True


class Range(NamedTuple):
    # [start, stop)
    start: int
    stop: int

    @property
    def width(self):
        assert self.start <= self.stop
        return self.stop - self.start

    def __add__(self, other: int):
            return Range(self.start + other, self.stop + other)


''' 가시화를 위한 영역 범위 '''
# 드론이 모니터링하는 영역의 x축 범위 (기본: 0 이상 100 미만)
DroneXRange = Range(0, 100)
# 에지 서버 배치 영역의 x축 범위 (기본: 100 이상 140 미만)
EdgeServerXRange = DroneXRange + 40
# 클라우드 서버 배치 영역의 x축 범위 (기본: 140 이상 200 미만)
CloudServerXRange = EdgeServerXRange + 60
# 전체 영역 너비, 높이
AreaXRange = Range(DroneXRange.start, CloudServerXRange.stop)
AreaYRange = Range(0, 100)

''' 통신 반경 파라미터 '''
DroneTransRange = 30  # 드론의 통신 반경 (기본: 100)
EdgeServerTransRange = math.inf
CloudServerTransRange = math.inf


''' 네트워크 토폴리지의 드론, 에지 서버, 클라우드 서버의 수 '''
NumOfDrones = 30  # UAV의 수 (기본: 30)
NumOfEdgeServer = 4  # 에지 서버의 수 (기본: 4)
NumOfCloudServer = 2  # 클라우드 서버의 수 (기본: 2)

''' 프로세싱 Rate 파라미터 '''
MaxProcessingRateOfDrone = 100  # 드론의 프로세싱 rate 파라미터 (기본: 100)
MaxProcessingRateOfEdgeServer = 500  # 에지 서버의 프로세싱 rate 파라미터 (기본: 500)
MaxProcessingRateOfCloudServer = 10000  # 클라우드 서버의 프로세싱 rate 파라미터 (기본: 10000)

''' 딜레이 Factor 파라미터 '''
MaxDelayFactorOfDrone = 1  # 드론의 딜레이 factor (기본: 1)
MaxDelayFactorOfEdgeServer = 5  # 에지 서버의 딜레이 factor (기본: 5)
MaxDelayFactorOfCloudServer = 6   # 클라우드 서버의 딜레이 factor (기본: 6)

''' 대역폭 파라미터 '''
BandwidthOfDrone = 200  # 드론의 대역폭 (기본: 200)
BandwidthOfEdgeServer = 400  # 에지 서버의 대역폭 (기본: 400)
BandwidthOfCloudServer = 1000  # 클라우드 서버의 대역폭 (기본: 1000)

''' 워크플로우 관련 파라미터 '''
NumOfWorkflows = 20  # 워크플로우 수 (기본: 4)
MinTasksPerWorkFlow = 4  # 하나의 워크플로우의 최소 태스크 수 (기본: 4)
MaxTasksPerWorkflow = 4  # 하나의 워크플로우의 최대 태스크 수 (기본: 4)
MinRequiredProcessingPower = 20  # 각 태스크의 최소 소모 프로세싱 파워 (기본: 50)
MaxRequiredProcessingPower = 30  # 각 태스크의 최대 소모 프로세싱 파워 (기본: 1000)
MinRequiredBandwidth = 20  # 각 태스크의 최소 대역폭 파워 (기본: 50)
MaxRequiredBandwidth = 30  # 각 태스크의 최대 대역폭 파워 (기본: 200)

# NodeXPositions = [0, ]  # 그래프로 각 노드 위치를 표기하기 위한 X좌표 배열
# NodeYPositions = [0, ]  # 그래프로 각 노드 위치를 표기하기 위한 Y좌표 배열
#
# MAX_MATRIX_INDEX = NumOfDrones + NumOfEdgeServer + NumOfCloudServer  # 네트워크 연결 정보 저장 테이블의 최대 인덱스
#
# ConnectionInfo = [[0 for _ in range(MAX_MATRIX_INDEX + 1)] for __ in range(MAX_MATRIX_INDEX + 1)]  # 네트워크 연결 정보 초기화
#
# NodePositionInfo = [(0, 0), ]  # 드론, 에지서버, 클라우드 서버의 위치 정보 저장
#
# ProcessingRateOfDEC = [0, ]  # 각 드론, 에지서버, 클라우드 서버의 프로세싱 rate 저장
#
# DelayFactorOfDEC = [0, ]  # 각 드론, 에지서버, 클라우드 서버의 딜레이 factor 저장
#
# BandwidthOfDEC = [0, ]  # 각 드론, 에지서버, 클라우서버의 대역폭 저장
#
# WorkflowInfo = [0, ]  # sequential 워크플로우 정보 저장 [(태스크 번호, 프로세싱 요구량, 대역폭요구량), ...]
#
# DeployedStatusOfWorkflows = [0, ]  # 각 워크플로우의 배치 여부
#
#
# # ==============================================
# MA_MAX_ITERATION = 100
