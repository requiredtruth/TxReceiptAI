import unittest
from txreceiptai.analyze import DecodeError, analyze_bundle, decode_calldata
from txreceiptai.explain import explain_local

def word(value: int) -> str:
    return f"{value:064x}"

class AnalyzeTests(unittest.TestCase):
    def bundle(self):
        tx_hash = "0x" + "ab" * 32
        tx = {"hash":tx_hash,"blockNumber":"0x10","from":"0x" + "aa" * 20,"to":"0x" + "bb" * 20,"value":"0x0","input":"0xa9059cbb" + word(0x1234) + word(500)}
        receipt = {"transactionHash":tx_hash,"blockNumber":"0x10","status":"0x1","gasUsed":"0x5208","effectiveGasPrice":"0x3b9aca00","logs":[]}
        return tx, receipt

    def test_decodes_transfer_and_fee(self) -> None:
        tx, receipt = self.bundle()
        evidence = analyze_bundle(tx, receipt)["evidence"]
        self.assertEqual(evidence["calldata"]["method"], "transfer(address,uint256)")
        self.assertEqual(evidence["calldata"]["arguments"]["amount"], 500)
        self.assertEqual(evidence["transaction_fee_wei"], 21000 * 1_000_000_000)

    def test_unknown_selector_stays_unknown(self) -> None:
        self.assertEqual(decode_calldata("0xdeadbeef")["method"], "unknown")

    def test_mismatched_receipt_fails(self) -> None:
        tx, receipt = self.bundle(); receipt["transactionHash"] = "0x" + "cd" * 32
        with self.assertRaisesRegex(DecodeError, "hashes do not match"):
            analyze_bundle(tx, receipt)

    def test_short_address_fails(self) -> None:
        tx, receipt = self.bundle(); tx["from"] = "0xAA"
        with self.assertRaisesRegex(DecodeError, "20-byte"):
            analyze_bundle(tx, receipt)

    def test_ai_endpoint_must_be_local(self) -> None:
        with self.assertRaisesRegex(ValueError, "loopback"):
            explain_local({}, "https://example.com", "model")

if __name__ == "__main__":
    unittest.main()
