export interface IResponse<T> {
  data: T,
  message: string,
  status: EStatus.Success | EStatus.Error; // 仅允许枚举中的 200 或 500
}

export enum EStatus {
  'Success' = 200,
  'Error' = 500
}