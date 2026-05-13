import { Layout } from "antd";
import { useMount } from "ahooks";
import { listTavernCharacters } from "@services/tauriApi";
export function AiTavernPage() {
  useMount(async () => {
    console.log(123);
    const res = await listTavernCharacters();
    console.log(res);
  });
  return (
    <Layout
      style={{
        height: "100%",
        minHeight: 640,
        background: "black",
      }}
    ></Layout>
  );
}
