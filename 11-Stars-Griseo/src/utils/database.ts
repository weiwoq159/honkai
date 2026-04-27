import { invokeRust } from "./invoke";

class InvokDatabase {
  async select_config_tables(keys: string) {
    const res = await invokeRust("select_config_tables", { keys });
    console.log(res);
    return res;
  }
}

const invokeDatabase = new InvokDatabase();

export default invokeDatabase;
